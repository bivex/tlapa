"""CLI application."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from swifta.application.dto import ParseDirectoryCommand, ParseFileCommand, ParsingJobReportDTO
from swifta.application.use_cases import ParsingJobService
from swifta.domain.errors import SwiftaError
from swifta.infrastructure.antlr.parser_adapter import AntlrTlaplusSyntaxParser
from swifta.infrastructure.filesystem.source_repository import FileSystemSourceRepository
from swifta.infrastructure.rendering.tlaplus_structure_renderer import (
    render_index_html,
    render_single_file,
)
from swifta.presentation.nassi_renderer import render_nassi_diagram
from swifta.infrastructure.system import (
    InMemoryParsingJobRepository,
    StructuredLoggingEventPublisher,
    SystemClock,
    configure_logging,
)


def main(argv: list[str] | None = None) -> int:
    parser = _build_argument_parser()
    args = parser.parse_args(argv)

    configure_logging(verbose=getattr(args, "verbose", False))

    try:
        if args.command == "parse-file":
            report = _build_parse_service().parse_file(ParseFileCommand(path=args.path))
            print(json.dumps(report.to_dict(), indent=2))
            return _exit_code_for(report)

        elif args.command == "parse-dir":
            report = _build_parse_service().parse_directory(
                ParseDirectoryCommand(root_path=args.path)
            )
            print(json.dumps(report.to_dict(), indent=2))
            return _exit_code_for(report)

        elif args.command == "nassi-file":
            return _nassi_file(args)

        elif args.command == "nassi-dir":
            return _nassi_dir(args)

        else:
            parser.error(f"unsupported command: {args.command}")

    except SwiftaError as error:
        print(json.dumps({"error": str(error)}, indent=2), file=sys.stderr)
        return 2

    return 0


def _nassi_file(args) -> int:
    from swifta.domain.model import SourceUnit, SourceUnitId, StructuralElementKind
    from swifta.presentation.nassi_builder import NassiBuilder

    source_path = Path(args.path).expanduser().resolve()
    content = source_path.read_text(encoding="utf-8")

    # Parse to get structural info
    parser = AntlrTlaplusSyntaxParser()
    source_unit = SourceUnit(
        identifier=SourceUnitId(source_path.stem),
        location=str(source_path),
        content=content,
    )
    outcome = parser.parse(source_unit)

    # Extract module name from first MODULE element
    module_name = source_path.stem
    for elem in outcome.structural_elements:
        if elem.kind == StructuralElementKind.MODULE:
            module_name = elem.name
            break

    # Build per-operator NSD diagrams
    builder = NassiBuilder()
    operator_diagrams = builder.build_all_operators(content)

    # Generate HTML with one SVG per operator
    svg_sections: list[str] = []
    for op_name, block_tree, line_no in operator_diagrams:
        svg = render_nassi_diagram(block_tree, op_name)
        svg_sections.append(
            f'<div class="operator">'
            f'<h2>{op_name} <span class="line">line {line_no}</span></h2>'
            f'{svg}'
            f'</div>'
        )

    out_path = _resolve_output_path(args.path, args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    operators_html = "\n".join(svg_sections) if svg_sections else "<p>No operator definitions found.</p>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>NSD — {module_name}</title>
<style>
:root{{--bg:#0d1117;--tx:#e6edf3;--accent:#58a6ff;--mono:"JetBrains Mono","Fira Code",monospace}}
body{{background:var(--bg);color:var(--tx);font-family:var(--mono);padding:24px;margin:0}}
h1{{font-size:20px;border-bottom:1px solid #30363d;padding-bottom:8px}}
.operator{{margin:24px 0 32px 0}}
h2{{font-size:15px;color:var(--accent);margin:0 0 8px 0}}
h2 .line{{color:#8b949e;font-weight:normal;font-size:12px}}
svg{{display:block;max-width:100%}}
</style>
</head>
<body>
<h1>NSD: {module_name}</h1>
<p>{len(operator_diagrams)} operator definitions &middot; {len(outcome.diagnostics)} diagnostics</p>
{operators_html}
</body>
</html>"""
    out_path.write_text(html, encoding="utf-8")

    payload = {
        "source_location": str(source_path),
        "module_name": module_name,
        "operator_count": len(operator_diagrams),
        "diagnostic_count": len(outcome.diagnostics),
        "output_path": str(out_path),
    }
    print(json.dumps(payload, indent=2))
    return 0


def _nassi_dir(args) -> int:
    root = Path(args.path).expanduser().resolve()
    output_dir = _resolve_output_directory(args.path, args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    tla_files = sorted(p for p in root.rglob("*.tla") if p.is_file())
    if not tla_files:
        print(json.dumps({"error": f"no .tla files found under {root}"}, indent=2), file=sys.stderr)
        return 2

    diagrams = []
    written = []

    for tla_path in tla_files:
        try:
            content = tla_path.read_text(encoding="utf-8")
            result = render_single_file(str(tla_path), content)
            diagrams.append(result)

            rel = tla_path.relative_to(root)
            out_html = (output_dir / rel).with_suffix(".html")
            out_html.parent.mkdir(parents=True, exist_ok=True)
            out_html.write_text(result.html, encoding="utf-8")

            written.append(
                {
                    "source_location": str(tla_path),
                    "module_name": result.module_name,
                    "element_count": result.element_count,
                    "diagnostic_count": result.diagnostic_count,
                    "output_path": str(out_html),
                    "relative_output_path": str(out_html.relative_to(output_dir)),
                }
            )
        except Exception as exc:
            written.append(
                {
                    "source_location": str(tla_path),
                    "error": str(exc),
                }
            )

    # Write index.html
    index_path = output_dir / "index.html"
    rel_paths = {
        w["source_location"]: w["relative_output_path"]
        for w in written
        if "relative_output_path" in w
    }
    index_path.write_text(render_index_html(str(root), diagrams, rel_paths), encoding="utf-8")

    payload = {
        "root_path": str(root),
        "output_dir": str(output_dir),
        "index_path": str(index_path),
        "file_count": len(tla_files),
        "module_count": len(diagrams),
        "total_elements": sum(d.element_count for d in diagrams),
        "documents": written,
    }
    print(json.dumps(payload, indent=2))
    return 0


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse TLA+ source code with ANTLR.")
    parser.add_argument("--verbose", action="store_true", help="Enable lifecycle logging.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pf = subparsers.add_parser("parse-file", help="Parse one TLA+ file.")
    pf.add_argument("path", help="Path to a .tla file.")

    pd = subparsers.add_parser("parse-dir", help="Parse all TLA+ files in a directory.")
    pd.add_argument("path", help="Path to a directory.")

    nf = subparsers.add_parser("nassi-file", help="Build a structure diagram for one TLA+ file.")
    nf.add_argument("path", help="Path to a .tla file.")
    nf.add_argument("--out", help="Output HTML path. Default: <input>.html")

    nd = subparsers.add_parser(
        "nassi-dir", help="Build structure diagrams for all TLA+ files in a directory."
    )
    nd.add_argument("path", help="Path to a directory.")
    nd.add_argument("--out", help="Output directory. Default: <input>.tlapa/")

    return parser


def _build_parse_service() -> ParsingJobService:
    return ParsingJobService(
        source_repository=FileSystemSourceRepository(),
        parser=AntlrTlaplusSyntaxParser(),
        event_publisher=StructuredLoggingEventPublisher(),
        clock=SystemClock(),
        job_repository=InMemoryParsingJobRepository(),
    )


def _exit_code_for(report: ParsingJobReportDTO) -> int:
    if report.summary.technical_failure_count > 0:
        return 1
    return 0


def _resolve_output_path(input_path: str, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path(input_path).expanduser().resolve().with_suffix(".html")


def _resolve_output_directory(input_path: str, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    resolved = Path(input_path).expanduser().resolve()
    return resolved.with_name(f"{resolved.name}.tlapa")


if __name__ == "__main__":
    raise SystemExit(main())
