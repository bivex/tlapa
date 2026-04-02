"""Render TLA+ module structure as Nassi-Shneiderman-style HTML."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from time import perf_counter

from swifta.domain.model import StructuralElement, SyntaxDiagnostic
from swifta.infrastructure.antlr.runtime import load_generated_types, parse_source_text


_KIND_COLORS = {
    "module": ("blue", "#1676dc", "#0b57ae"),
    "extends": ("green", "#2d9d4a", "#1e7a36"),
    "variable": ("purple", "#9b59b6", "#7d3c98"),
    "constant": ("purple", "#9b59b6", "#7d3c98"),
    "operator_definition": ("teal", "#1abc9c", "#148f77"),
    "function_definition": ("teal", "#1abc9c", "#148f77"),
    "module_definition": ("teal", "#1abc9c", "#148f77"),
    "recursive": ("amber", "#f39c12", "#d68910"),
    "instance": ("amber", "#f39c12", "#d68910"),
    "assumption": ("red", "#e74c3c", "#c0392b"),
    "theorem": ("red", "#e74c3c", "#c0392b"),
    "proof": ("blue", "#3498db", "#2980b9"),
    "use": ("green", "#27ae60", "#1e8449"),
    "hide": ("green", "#27ae60", "#1e8449"),
}

_KIND_ICONS = {
    "module": "M",
    "extends": "E",
    "variable": "x",
    "constant": "C",
    "operator_definition": "=",
    "function_definition": "f",
    "module_definition": "D",
    "recursive": "R",
    "instance": "I",
    "assumption": "A",
    "theorem": "T",
    "proof": "P",
}


@dataclass(frozen=True, slots=True)
class DiagramResult:
    source_location: str
    module_name: str
    element_count: int
    diagnostic_count: int
    elapsed_ms: float
    token_count: int
    html: str
    elements: tuple[StructuralElement, ...]
    diagnostics: tuple[SyntaxDiagnostic, ...]


def _depth_badge(i: int) -> str:
    if i <= 0:
        return ""
    if i <= 20:
        return f" {chr(0x2460 + i - 1)}"
    if i <= 35:
        return f" {chr(0x3251 + i - 21)}"
    return f" {chr(0x32B1 + i - 36)}"


def _render_element_block(element: StructuralElement, depth: int) -> str:
    kind = str(element.kind) if hasattr(element.kind, "value") else element.kind
    palette = _KIND_COLORS.get(kind, ("gray", "#7f8c8d", "#616a6b"))
    _color_name, bg, border = palette
    icon = _KIND_ICONS.get(kind, "-")
    badge = _depth_badge(depth)
    sig = escape(element.signature) if element.signature else ""
    name = escape(element.name)

    label_parts = []
    label_parts.append(f'<span class="icon">{icon}</span>')
    label_parts.append(f'<span class="name">{name}</span>')
    if badge:
        label_parts.append(f'<span class="badge">{badge}</span>')

    meta_parts = []
    if sig:
        meta_parts.append(f"<code>{sig}</code>")
    if element.container:
        meta_parts.append(f"<span>in {escape(element.container)}</span>")
    meta_parts.append(f'<span class="loc">L{element.line}</span>')

    return (
        f'<div class="block" style="border-left: 4px solid {border};">'
        f'<div class="block-header" style="background: {bg}22;">'
        f"{''.join(label_parts)}"
        f'<span class="kind-tag" style="background: {bg};">{escape(kind)}</span>'
        f"</div>"
        f'<div class="block-meta">{"".join(meta_parts)}</div>'
        f"</div>"
    )


def _extract_elements(
    content: str, generated=None
) -> tuple[
    tuple[StructuralElement, ...],
    tuple[SyntaxDiagnostic, ...],
    float,
    int,
]:
    """Parse TLA+ content and extract structural elements."""
    gen = generated or load_generated_types()

    t0 = perf_counter()
    result = parse_source_text(content, gen)
    elapsed_ms = round((perf_counter() - t0) * 1000, 3)

    from swifta.infrastructure.antlr.parser_adapter import _build_structure_visitor

    visitor = _build_structure_visitor(gen.visitor_type)()
    visitor.visit(result.tree)

    return (
        tuple(visitor.elements),
        result.diagnostics,
        elapsed_ms,
        len(result.token_stream.tokens),
    )


def render_single_file(source_path: str, content: str, generated=None) -> DiagramResult:
    """Parse and render a single TLA+ file as HTML."""
    elements, diagnostics, elapsed_ms, token_count = _extract_elements(content, generated)

    module_name = "TLA+ Module"
    for elem in elements:
        if str(elem.kind) in ("module", "StructuralElementKind.MODULE"):
            module_name = elem.name
            break

    html = _render_html_page(
        source_path, module_name, elements, diagnostics, elapsed_ms, token_count
    )

    return DiagramResult(
        source_location=source_path,
        module_name=module_name,
        element_count=len(elements),
        diagnostic_count=len(diagnostics),
        elapsed_ms=elapsed_ms,
        token_count=token_count,
        html=html,
        elements=elements,
        diagnostics=diagnostics,
    )


def _render_html_page(
    source_path: str,
    module_name: str,
    elements: tuple[StructuralElement, ...],
    diagnostics: tuple[SyntaxDiagnostic, ...],
    elapsed_ms: float,
    token_count: int,
) -> str:
    kind_counts: dict[str, int] = {}
    for elem in elements:
        k = str(elem.kind) if hasattr(elem.kind, "value") else elem.kind
        kind_counts[k] = kind_counts.get(k, 0) + 1

    summary_items = "".join(
        f'<span class="chip" style="border-color: {_KIND_COLORS.get(k, ("gray", "#7f8c8d", "#616a6b"))[1]};'
        f'background: {_KIND_COLORS.get(k, ("gray", "#7f8c8d", "#616a6b"))[1]}33;">'
        f"{v} {escape(k.replace('_', ' '))}</span>"
        for k, v in sorted(kind_counts.items())
    )

    diag_html = ""
    if diagnostics:
        rows = "".join(
            f'<tr><td class="sev">{"ERR" if str(d.severity) in ("error", "DiagnosticSeverity.ERROR") else "WRN"}</td>'
            f"<td>L{d.line}:{d.column}</td><td>{escape(d.message)}</td></tr>"
            for d in diagnostics
        )
        diag_html = (
            f'<details class="diags"><summary>{len(diagnostics)} diagnostic(s)</summary>'
            f"<table><thead><tr><th></th><th>Loc</th><th>Message</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></details>"
        )

    blocks = []
    for elem in elements:
        kind = str(elem.kind) if hasattr(elem.kind, "value") else elem.kind
        if kind in ("module",):
            depth = 0
        elif kind in ("theorem", "assumption", "proof"):
            depth = 2
        else:
            depth = 1
        blocks.append(_render_element_block(elem, depth))

    if not blocks:
        blocks.append('<div class="block"><div class="block-header">No elements found</div></div>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TLA+ Structure — {escape(module_name)}</title>
<style>
:root{{--bg:#0d1117;--sf:#161b22;--sf2:#21262d;--bd:#30363d;--tx:#e6edf3;--tm:#8b949e;--bl:#1676dc}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"IBM Plex Sans",-apple-system,sans-serif;background:var(--bg);color:var(--tx);padding:24px;max-width:960px;margin:0 auto}}
.hdr{{margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid var(--bd)}}
.hdr h1{{font-size:22px;font-weight:600;margin-bottom:4px}}
.hdr .meta{{font-size:13px;color:var(--tm);font-family:monospace}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}}
.chip{{padding:4px 10px;border-radius:12px;font-size:12px;font-weight:500;border:1px solid}}
.diags{{margin-bottom:16px;background:var(--sf);border:1px solid var(--bd);border-radius:8px;padding:12px}}
.diags summary{{cursor:pointer;color:#e74c3c;font-weight:500;margin-bottom:6px}}
.diags table{{width:100%;border-collapse:collapse;font-size:13px}}
.diags th,.diags td{{text-align:left;padding:5px 8px;border-bottom:1px solid var(--bd)}}
.sev{{color:#e74c3c;font-weight:600;font-size:11px;text-transform:uppercase}}
.str{{display:flex;flex-direction:column;gap:6px}}
.block{{background:var(--sf);border-radius:6px;overflow:hidden}}
.block:hover{{transform:translateX(2px);transition:transform .1s}}
.block-header{{display:flex;align-items:center;gap:8px;padding:10px 14px;font-size:14px;font-weight:500}}
.block-header .icon{{font-family:monospace;font-weight:700;font-size:13px;width:20px;text-align:center;background:var(--sf2);border-radius:4px;padding:2px 0}}
.block-header .name{{font-family:monospace;font-weight:600;font-size:14px}}
.block-header .badge{{color:var(--tm);font-size:14px}}
.block-header .kind-tag{{margin-left:auto;padding:2px 8px;border-radius:8px;font-size:10px;font-weight:600;color:#fff;text-transform:uppercase;letter-spacing:.04em}}
.block-meta{{padding:4px 14px 8px 52px;font-size:12px;color:var(--tm);display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
.block-meta code{{font-family:monospace;font-size:12px;color:var(--tx);background:var(--sf2);padding:2px 6px;border-radius:4px}}
.block-meta .loc{{font-family:monospace;font-size:11px}}
</style>
</head>
<body>
<div class="hdr"><h1>{escape(module_name)}</h1>
<div class="meta">{escape(source_path)} &middot; {token_count} tok &middot; {elapsed_ms:.1f}ms</div></div>
<div class="chips">{summary_items}</div>
{diag_html}
<div class="str">
{"".join(blocks)}
</div>
</body></html>"""


def render_index_html(
    root_path: str,
    diagrams: list[DiagramResult],
) -> str:
    """Render an index HTML page linking to individual diagram files."""
    rows = "".join(
        f"<tr>"
        f'<td><a href="{escape(_relative_name(d.source_location, root_path))}.html">'
        f"{escape(_relative_name(d.source_location, root_path))}</a></td>"
        f"<td>{escape(d.module_name)}</td>"
        f"<td>{d.element_count}</td>"
        f"<td>{d.diagnostic_count}</td>"
        f"<td>{d.elapsed_ms:.0f}ms</td>"
        f"</tr>"
        for d in diagrams
    )
    if not rows:
        rows = '<tr><td colspan="5">No .tla files found.</td></tr>'

    total_elements = sum(d.element_count for d in diagrams)
    total_diag = sum(d.diagnostic_count for d in diagrams)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TLA+ Structure — {escape(root_path)}</title>
<style>
:root{{--bg:#0d1117;--sf:#161b22;--bd:#30363d;--tx:#e6edf3;--tm:#8b949e;--bl:#1676dc}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"IBM Plex Sans",-apple-system,sans-serif;background:var(--bg);color:var(--tx);padding:24px;max-width:1000px;margin:0 auto}}
.hdr{{margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid var(--bd)}}
.hdr h1{{font-size:22px;font-weight:600}}
.hdr .meta{{font-size:13px;color:var(--tm);font-family:monospace;margin-top:4px}}
.stats{{display:flex;gap:16px;margin-bottom:20px}}
.stat{{background:var(--sf);border:1px solid var(--bd);border-radius:8px;padding:12px 20px;text-align:center}}
.stat .num{{font-size:28px;font-weight:700;color:var(--bl)}}
.stat .label{{font-size:12px;color:var(--tm);margin-top:2px}}
table{{width:100%;border-collapse:collapse;background:var(--sf);border-radius:8px;overflow:hidden}}
thead th{{background:var(--bl);color:#fff;font-size:12px;text-transform:uppercase;letter-spacing:.05em;padding:10px 14px;text-align:left}}
tbody td{{padding:10px 14px;border-bottom:1px solid var(--bd);font-size:14px}}
tbody tr:hover{{background:#1c2333}}
a{{color:var(--bl);text-decoration:none;font-weight:600;font-family:monospace}}
a:hover{{text-decoration:underline}}
td:nth-child(3),td:nth-child(4),td:nth-child(5){{text-align:right;font-family:monospace}}
</style>
</head>
<body>
<div class="hdr">
<h1>TLA+ Structure Diagrams</h1>
<div class="meta">{escape(root_path)}</div>
</div>
<div class="stats">
<div class="stat"><div class="num">{len(diagrams)}</div><div class="label">modules</div></div>
<div class="stat"><div class="num">{total_elements}</div><div class="label">elements</div></div>
<div class="stat"><div class="num">{total_diag}</div><div class="label">diagnostics</div></div>
</div>
<table>
<thead><tr><th>Source</th><th>Module</th><th>Elements</th><th>Diags</th><th>Time</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body></html>"""


def _relative_name(source_location: str, root_path: str) -> str:
    try:
        return Path(source_location).relative_to(Path(root_path)).as_posix()
    except ValueError:
        return Path(source_location).name
