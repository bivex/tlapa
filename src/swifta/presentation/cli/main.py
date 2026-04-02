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
    source_path = Path(args.path).expanduser().resolve()
    content = source_path.read_text(encoding="utf-8")

    result = render_single_file(str(source_path), content)

    out_path = _resolve_output_path(args.path, args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result.html, encoding="utf-8")

    payload = {
        "source_location": result.source_location,
        "module_name": result.module_name,
        "element_count": result.element_count,
        "diagnostic_count": result.diagnostic_count,
        "elapsed_ms": result.elapsed_ms,
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
    index_path.write_text(render_index_html(str(root), diagrams), encoding="utf-8")

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
