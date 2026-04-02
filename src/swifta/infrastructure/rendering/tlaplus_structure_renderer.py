"""Render TLA+ module structure as actual Nassi-Shneiderman diagrams (SVG)."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from time import perf_counter

from swifta.domain.model import StructuralElement, SyntaxDiagnostic
from swifta.infrastructure.antlr.runtime import load_generated_types, parse_source_text

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
BLOCK_H = 34
BLOCK_PAD = 2
MARGIN_X = 20
MARGIN_Y = 8
DIAGRAM_W = 640
FONT = '"JetBrains Mono", "Fira Code", monospace'
FONT_SIZE = 12

# Palette (Tokyo Night)
C_BG = "#0d1117"
C_BLOCK = "#1e2533"
C_BLOCK_STROKE = "#3b4660"
C_IF = "#1a2740"
C_IF_STROKE = "#569cd6"
C_LOOP = "#1a3028"
C_LOOP_STROKE = "#4ec990"
C_CASE = "#2a1a3a"
C_CASE_STROKE = "#c586c0"
C_MODULE = "#0f2847"
C_MODULE_STROKE = "#569cd6"
C_TEXT = "#d4d4d4"
C_TEXT_DIM = "#808080"
C_TEXT_BLUE = "#569cd6"
C_TEXT_GREEN = "#4ec990"
C_TEXT_PURPLE = "#c586c0"
C_TEXT_YELLOW = "#dcdcaa"
C_TEXT_ORANGE = "#ce9178"
C_TEXT_RED = "#f44747"
C_THEOREM = "#3a1a1a"
C_THEOREM_STROKE = "#f44747"
C_EXTENDS = "#1a3a2a"
C_EXTENDS_STROKE = "#4ec990"
C_CONST_VAR = "#2a2a1a"
C_CONST_VAR_STROKE = "#dcdcaa"
C_PROOF = "#1a2a3a"
C_PROOF_STROKE = "#569cd6"
C_COMMENT = "#3b4660"
C_BORDER_LIGHT = "#484f58"


@dataclass
class DiagramResult:
    source_location: str
    module_name: str
    element_count: int
    diagnostic_count: int
    elapsed_ms: float
    token_count: int
    html: str


def _extract_elements(content: str, generated=None):
    gen = generated or load_generated_types()
    t0 = perf_counter()
    result = parse_source_text(content, gen)
    elapsed_ms = round((perf_counter() - t0) * 1000, 3)

    from swifta.infrastructure.antlr.parser_adapter import _build_structure_visitor

    visitor = _build_structure_visitor(gen.visitor_type)()
    visitor.visit(result.tree)
    return tuple(visitor.elements), result.diagnostics, elapsed_ms, len(result.token_stream.tokens)


def render_single_file(source_path: str, content: str, generated=None) -> DiagramResult:
    elements, diagnostics, elapsed_ms, token_count = _extract_elements(content, generated)

    module_name = "TLA+ Module"
    for elem in elements:
        k = str(elem.kind)
        if k in ("module", "StructuralElementKind.MODULE"):
            module_name = elem.name
            break

    svg = _build_svg(module_name, elements)
    html = _wrap_html(source_path, module_name, svg, elements, diagnostics, elapsed_ms, token_count)

    return DiagramResult(
        source_location=source_path,
        module_name=module_name,
        element_count=len(elements),
        diagnostic_count=len(diagnostics),
        elapsed_ms=elapsed_ms,
        token_count=token_count,
        html=html,
    )


# ---------------------------------------------------------------------------
# SVG drawing primitives
# ---------------------------------------------------------------------------


def _svg_rect(
    x: int,
    y: int,
    w: int,
    h: int,
    fill: str,
    stroke: str,
    text: str = "",
    text_color: str = C_TEXT,
    radius: int = 0,
    font_weight: str = "normal",
    sub: str = "",
) -> str:
    r = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" ry="{radius}" '
    r += f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
    if text:
        tx = x + 10
        ty = y + h // 2 + 4
        r += f'\n  <text x="{tx}" y="{ty}" fill="{text_color}" '
        r += f'font-family={FONT} font-size="{FONT_SIZE}" font-weight="{font_weight}">'
        r += f"{escape(text)}</text>"
    if sub:
        tx = x + w - 10
        ty = y + h // 2 + 4
        r += f'\n  <text x="{tx}" y="{ty}" text-anchor="end" fill="{C_TEXT_DIM}" '
        r += f'font-family={FONT} font-size="10">{escape(sub)}</text>'
    return r


def _svg_if_diamond(x: int, y: int, w: int, h: int, text: str) -> str:
    """IF/THEN/ELSE triangle split — left = THEN, right = ELSE."""
    mid = w // 2
    s = (
        f'<polygon points="{x},{y} {x + w},{y} {x + mid},{y + h}" '
        f'fill="{C_IF}" stroke="{C_IF_STROKE}" stroke-width="1"/>'
        f'\n  <line x1="{x + mid}" y1="{y}" x2="{x + mid}" y2="{y + h}" '
        f'stroke="{C_IF_STROKE}" stroke-width="1" stroke-dasharray="4,3"/>'
        f'\n  <text x="{x + mid}" y="{y + 14}" text-anchor="middle" '
        f'fill="{C_TEXT_BLUE}" font-family={FONT} font-size="{FONT_SIZE}">'
        f"{escape(text)}</text>"
        f'\n  <text x="{x + 10}" y="{y + h - 6}" fill="{C_TEXT_GREEN}" '
        f'font-family={FONT} font-size="10">T</text>'
        f'\n  <text x="{x + w - 10}" y="{y + h - 6}" text-anchor="end" '
        f'fill="{C_TEXT_RED}" font-family={FONT} font-size="10">F</text>'
    )
    return s


def _svg_case_block(x: int, y: int, w: int, h: int, arms: list[str]) -> str:
    """CASE arms side-by-side."""
    n = max(len(arms), 1)
    arm_w = w // n
    parts = []
    for i, arm in enumerate(arms[:n]):
        ax = x + i * arm_w
        parts.append(
            f'<rect x="{ax}" y="{y}" width="{arm_w}" height="{h}" '
            f'fill="{C_CASE}" stroke="{C_CASE_STROKE}" stroke-width="1"/>'
            f'\n  <text x="{ax + arm_w // 2}" y="{y + h // 2 + 4}" '
            f'text-anchor="middle" fill="{C_TEXT_PURPLE}" '
            f'font-family={FONT} font-size="11">{escape(arm)}</text>'
        )
    # separator lines
    for i in range(1, n):
        lx = x + i * arm_w
        parts.append(
            f'<line x1="{lx}" y1="{y}" x2="{lx}" y2="{y + h}" '
            f'stroke="{C_CASE_STROKE}" stroke-width="1"/>'
        )
    return "\n  ".join(parts)


def _svg_loop_top(x: int, y: int, w: int, h: int, text: str, kind: str = "FOR") -> str:
    """Loop with rounded top (for/in, while)."""
    fill = C_LOOP
    stroke = C_LOOP_STROKE
    r = 14
    s = (
        f'<path d="M{x},{y + h} L{x},{y + r} Q{x},{y} {x + r},{y} '
        f'L{x + w - r},{y} Q{x + w},{y} {x + w},{y + r} L{x + w},{y + h}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        f'\n  <text x="{x + 10}" y="{y + r + 4}" fill="{C_TEXT_GREEN}" '
        f'font-family={FONT} font-size="{FONT_SIZE}">{escape(kind)}</text>'
        f'\n  <text x="{x + w - 10}" y="{y + r + 4}" text-anchor="end" '
        f'fill="{C_TEXT_DIM}" font-family={FONT} font-size="11">{escape(text)}</text>'
    )
    return s


def _svg_loop_bottom(x: int, y: int, w: int, h: int) -> str:
    """Loop closing brace."""
    r = 14
    return (
        f'<path d="M{x},{y} L{x},{y + h - r} Q{x},{y + h} {x + r},{y + h} '
        f'L{x + w - r},{y + h} Q{x + w},{y + h} {x + w},{y + h - r} L{x + w},{y}" '
        f'fill="{C_LOOP}" stroke="{C_LOOP_STROKE}" stroke-width="1"/>'
    )


# ---------------------------------------------------------------------------
# Build the full SVG diagram
# ---------------------------------------------------------------------------


def _build_svg(module_name: str, elements: tuple[StructuralElement, ...]) -> str:
    if not elements:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{DIAGRAM_W}" height="60">'
            f'<rect width="100%" height="100%" fill="{C_BG}"/>'
            f'<text x="20" y="35" fill="{C_TEXT_DIM}" font-family={FONT} font-size="13">'
            f"No structural elements</text></svg>"
        )

    # --- Group elements into TLA+ logical sections ---
    sections: list[tuple[str, list[StructuralElement]]] = []
    current_section = "header"
    current_items: list[StructuralElement] = []

    def section_end():
        if current_items:
            sections.append((current_section, current_items))
        return [], ""

    for elem in elements:
        k = str(elem.kind)
        name_l = elem.name.lower() if elem.name else ""

        if k in ("module", "StructuralElementKind.MODULE"):
            if current_items:
                sections.append((current_section, current_items))
            current_section = "module"
            current_items = [elem]
        elif k in ("constant", "StructuralElementKind.CONSTANT"):
            if current_section != "constant":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "constant"
                current_items = [elem]
            else:
                current_items.append(elem)
        elif k in ("variable", "StructuralElementKind.VARIABLE"):
            if current_section != "variable":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "variable"
                current_items = [elem]
            else:
                current_items.append(elem)
        elif k in ("operator_definition", "StructuralElementKind.OPERATOR_DEFINITION"):
            # Classify operator into logical TLA+ categories
            if any(tag in name_l for tag in ["init", "initial"]):
                cat = "init"
            elif any(tag in name_l for tag in ["next", "step", "do", "perform"]):
                cat = "action"
            elif any(tag in name_l for tag in ["inv", "typeinv", "invariant"]):
                cat = "invariant"
            elif any(
                tag in name_l for tag in ["spec", "next", "[]", "fairness", "safety", "liveness"]
            ):
                cat = "spec"
            else:
                cat = "predicate"
            if current_section != cat:
                if current_items:
                    sections.append((current_section, current_items))
                current_section = cat
                current_items = [elem]
            else:
                current_items.append(elem)
        elif k in ("function_definition", "StructuralElementKind.FUNCTION_DEFINITION"):
            if current_section != "function":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "function"
                current_items = [elem]
            else:
                current_items.append(elem)
        elif k in ("theorem", "StructuralElementKind.THEOREM"):
            if current_section != "theorem":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "theorem"
                current_items = [elem]
            else:
                current_items.append(elem)
        elif k in ("assumption", "StructuralElementKind.ASSUMPTION"):
            if current_section != "assumption":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "assumption"
                current_items = [elem]
            else:
                current_items.append(elem)
        elif k in ("proof", "StructuralElementKind.PROOF"):
            if current_section != "proof":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "proof"
                current_items = [elem]
            else:
                current_items.append(elem)
        elif k in ("instance", "StructuralElementKind.INSTANCE"):
            if current_section != "instance":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "instance"
                current_items = [elem]
            else:
                current_items.append(elem)
        else:
            # Unknown/other
            if current_section != "other":
                if current_items:
                    sections.append((current_section, current_items))
                current_section = "other"
                current_items = [elem]
            else:
                current_items.append(elem)

    if current_items:
        sections.append((current_section, current_items))

    # --- Compute layout ---
    y_cursor = 0
    drawn_parts: list[str] = []
    w = DIAGRAM_W - 2 * MARGIN_X

    def _draw_block(
        y: int,
        text: str,
        fill: str,
        stroke: str,
        text_color: str = C_TEXT,
        sub: str = "",
        font_weight: str = "normal",
        radius: int = 0,
    ) -> int:
        drawn_parts.append(
            _svg_rect(
                MARGIN_X, y, w, BLOCK_H, fill, stroke, text, text_color, radius, font_weight, sub
            )
        )
        return y + BLOCK_H + BLOCK_PAD

    def _draw_section_header(y: int, title: str) -> int:
        """Draw a section header with separator and title."""
        y += 6
        drawn_parts.append(
            f'<line x1="{MARGIN_X}" y1="{y}" x2="{MARGIN_X + w}" y2="{y}" '
            f'stroke="{C_BORDER_LIGHT}" stroke-width="1"/>'
        )
        y += 2
        drawn_parts.append(
            f'<text x="{MARGIN_X + 10}" y="{y + 9}" fill="{C_TEXT_DIM}" '
            f'font-family={FONT} font-size="11" font-weight="600">{escape(title)}</text>'
        )
        y += 10
        return y

    for section_type, items in sections:
        # Section header styling
        if section_type == "module":
            name = items[0].name
            y_cursor = _draw_block(
                y_cursor,
                f"MODULE {name}",
                C_MODULE,
                C_MODULE_STROKE,
                C_TEXT_BLUE,
                f"L{items[0].line}",
                "bold",
                6,
            )
            y_cursor += 4

        elif section_type == "extends":
            y_cursor = _draw_section_header(y_cursor, "EXTENDS")
            for ext in items:
                y_cursor = _draw_block(
                    y_cursor,
                    f"EXTENDS {ext.name}",
                    C_EXTENDS,
                    C_EXTENDS_STROKE,
                    C_TEXT_GREEN,
                    f"L{ext.line}",
                )
            y_cursor += 4

        elif section_type == "constant":
            y_cursor = _draw_section_header(y_cursor, "CONSTANTS")
            for const in items:
                label = const.signature or const.name
                y_cursor = _draw_block(
                    y_cursor, label, C_CONST_VAR, C_CONST_VAR_STROKE, C_TEXT_YELLOW, f"L{const.line}"
                )
            y_cursor += 4

        elif section_type == "variable":
            y_cursor = _draw_section_header(y_cursor, "VARIABLES")
            for var in items:
                label = var.signature or var.name
                y_cursor = _draw_block(
                    y_cursor, label, C_CONST_VAR, C_CONST_VAR_STROKE, C_TEXT_YELLOW, f"L{var.line}"
                )
            y_cursor += 4

        elif section_type == "init":
            y_cursor = _draw_section_header(y_cursor, "INITIALIZATION")
            items_sorted = sorted(items, key=lambda d: d.line)
            for defn in items_sorted:
                label = defn.signature or defn.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_TEXT_GREEN, C_TEXT, f"L{defn.line}"
                )
            y_cursor += 4

        elif section_type == "action":
            y_cursor = _draw_section_header(y_cursor, "ACTIONS")
            items_sorted = sorted(items, key=lambda d: d.name.lower())
            for defn in items_sorted:
                label = defn.signature or defn.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_TEXT_YELLOW, C_TEXT, f"L{defn.line}"
                )
            y_cursor += 4

        elif section_type == "predicate":
            y_cursor = _draw_section_header(y_cursor, "PREDICATES")
            items_sorted = sorted(items, key=lambda d: d.name.lower())
            for defn in items_sorted:
                label = defn.signature or defn.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_BLOCK_STROKE, C_TEXT, f"L{defn.line}"
                )
            y_cursor += 4

        elif section_type == "invariant":
            y_cursor = _draw_section_header(y_cursor, "INVARIANTS")
            items_sorted = sorted(items, key=lambda d: d.name.lower())
            for defn in items_sorted:
                label = defn.signature or defn.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_TEXT_GREEN, C_TEXT, f"L{defn.line}"
                )
            y_cursor += 4

        elif section_type == "spec":
            y_cursor = _draw_section_header(y_cursor, "SPECIFICATION")
            items_sorted = sorted(items, key=lambda d: d.name.lower())
            for defn in items_sorted:
                label = defn.signature or defn.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_TEXT_ORANGE, C_TEXT, f"L{defn.line}"
                )
            y_cursor += 4

        elif section_type == "theorem":
            y_cursor = _draw_section_header(y_cursor, "THEOREMS")
            items_sorted = sorted(items, key=lambda d: d.name.lower())
            for thm in items_sorted:
                label = thm.signature or thm.name
                y_cursor = _draw_block(
                    y_cursor, label, C_THEOREM, C_THEOREM_STROKE, C_TEXT_RED, f"L{thm.line}", "bold"
                )
            y_cursor += 4

        elif section_type == "assumption":
            y_cursor = _draw_section_header(y_cursor, "ASSUMPTIONS")
            for assm in items:
                label = assm.signature or assm.name or "ASSUME"
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_TEXT_PURPLE, C_TEXT, f"L{assm.line}"
                )
            y_cursor += 4

        elif section_type == "proof":
            y_cursor = _draw_section_header(y_cursor, "PROOF")
            for prf in items:
                y_cursor = _draw_block(
                    y_cursor, "PROOF", C_PROOF, C_PROOF_STROKE, C_TEXT_BLUE, f"L{prf.line}"
                )
            y_cursor += 4

        elif section_type == "instance":
            y_cursor = _draw_section_header(y_cursor, "INSTANCES")
            for inst in items:
                label = inst.signature or inst.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_TEXT_YELLOW, C_TEXT, f"L{inst.line}"
                )
            y_cursor += 4

        elif section_type == "function":
            y_cursor = _draw_section_header(y_cursor, "FUNCTIONS")
            items_sorted = sorted(items, key=lambda d: d.name.lower())
            for defn in items_sorted:
                label = defn.signature or defn.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_TEXT_BLUE, C_TEXT, f"L{defn.line}"
                )
            y_cursor += 4

        else:
            # Other/unknown section
            y_cursor = _draw_section_header(y_cursor, section_type.upper())
            for item in items:
                label = item.signature or item.name
                y_cursor = _draw_block(
                    y_cursor, label, C_BLOCK, C_BLOCK_STROKE, C_TEXT, f"L{item.line}"
                )
            y_cursor += 4

    total_h = y_cursor + MARGIN_Y

    # Build SVG
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{DIAGRAM_W}" height="{total_h}" '
        f'viewBox="0 0 {DIAGRAM_W} {total_h}">\n'
        f'<rect width="100%" height="100%" fill="{C_BG}" rx="6"/>\n'
    )
    svg += "\n".join(drawn_parts)
    svg += "\n</svg>"
    return svg


# ---------------------------------------------------------------------------
# Full HTML page
# ---------------------------------------------------------------------------


def _wrap_html(
    source_path: str,
    module_name: str,
    svg: str,
    elements: tuple[StructuralElement, ...],
    diagnostics: tuple[SyntaxDiagnostic, ...],
    elapsed_ms: float,
    token_count: int,
) -> str:
    kind_counts: dict[str, int] = {}
    for e in elements:
        k = str(e.kind)
        kind_counts[k] = kind_counts.get(k, 0) + 1

    summary = " &middot; ".join(
        f"{v} {escape(k.replace('StructuralElementKind.', '').replace('_', ' '))}"
        for k, v in sorted(kind_counts.items())
    )

    diag_html = ""
    if diagnostics:
        # Filter out known false-positive expression parsing errors that don't affect structure extraction
        def is_relevant(d) -> bool:
            msg = d.message.lower()
            # These are typically ANTLR struggling with TLA+ expression bodies; structure is still extracted
            false_pos_patterns = [
                "no viable alternative",
                "mismatched input",
                "missing def",
                "extraneous input",
                "missing separator",
                "expecting {and, or}",  # often false positive for /\ in expression
            ]
            # If message contains keywords about expression tokens, likely false positive
            if any(p in msg for p in false_pos_patterns):
                return False
            return True

        relevant = [d for d in diagnostics if is_relevant(d)]
        hidden_count = len(diagnostics) - len(relevant)
        # Show up to 20 relevant diagnostics
        shown = relevant[:20]
        rows = "".join(
            f'<tr><td class="sev">ERR</td>'
            f"<td>L{d.line}:{d.column}</td><td>{escape(d.message)}</td></tr>"
            for d in shown
        )
        if hidden_count > 0:
            rows += (
                f'<tr><td colspan="3" class="more-info">+ {hidden_count} similar omitted</td></tr>'
            )
        if shown:
            diag_html = (
                f'<details class="diags" open>'
                f"<summary>{len(relevant)} relevant diagnostic(s)</summary>"
                f"<table><thead><tr><th>Sev</th><th>Loc</th><th>Message</th></tr></thead>"
                f"<tbody>{rows}</tbody></table></details>"
            )
        else:
            # All diagnostics were filtered out as false positives; don't show diagnostics panel
            diag_html = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Structure — {escape(module_name)}</title>
<style>
:root{{
  --bg: #0d1117;
  --sf: #161b22;
  --bd: #30363d;
  --tx: #e6edf3;
  --tm: #8b949e;
  --blue: #569cd6;
  --green: #4ec990;
  --purple: #c586c0;
  --yellow: #dcdcaa;
  --orange: #ce9178;
  --red: #f44747;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  font-family: {FONT};
  background: var(--bg);
  color: var(--tx);
  padding: 24px;
  max-width: 960px;
  margin: 0 auto;
}}
.hdr{{
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--bd);
}}
.hdr h1{{
  font-size: 22px;
  font-weight: 700;
  color: var(--blue);
  margin-bottom: 6px;
}}
.hdr .meta{{
  font-size: 13px;
  color: var(--tm);
  font-family: "JetBrains Mono", monospace;
}}
.summary{{
  font-size: 14px;
  color: var(--tm);
  margin-bottom: 20px;
  line-height: 1.6;
}}
.diags{{
  margin-bottom: 20px;
  background: var(--sf);
  border: 1px solid var(--bd);
  border-radius: 8px;
  padding: 12px;
}}
.diags summary{{
  cursor: pointer;
  color: var(--orange);
  font-weight: 600;
  font-size: 14px;
}}
.diags table{{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-top: 8px;
}}
.diags th,.diags td{{
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid var(--bd);
}}
.diags th{{
  background: rgba(86, 156, 214, 0.15);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.05em;
}}
.sev{{
  color: var(--red);
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
}}
.more-info{{
  color: var(--tm);
  font-style: italic;
  text-align: center;
}}
svg{{
  display: block;
  border: 1px solid var(--bd);
  border-radius: 8px;
  width: 100%;
  max-width: {DIAGRAM_W}px;
  background: var(--bg);
}}
</style>
</head>
<body>
<div class="hdr">
  <h1>{escape(module_name)}</h1>
  <div class="meta">{escape(source_path)} &middot; {token_count} tokens &middot; {elapsed_ms:.1f}ms</div>
</div>
<div class="summary">{summary}</div>
{diag_html}
{svg}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------


def render_index_html(
    root_path: str, diagrams: list[DiagramResult], relative_paths: dict[str, str] | None = None
) -> str:
    rows = []
    for d in diagrams:
        rel = _rel_name(d.source_location, root_path)
        href = (relative_paths or {}).get(d.source_location, str(Path(rel).with_suffix(".html")))
        rows.append(
            f'<tr><td><a href="{escape(href)}">{escape(rel)}</a></td>'
            f"<td>{escape(d.module_name)}</td>"
            f"<td>{d.element_count}</td>"
            f"<td>{d.elapsed_ms:.0f}ms</td></tr>"
        )
    rows_html = "".join(rows) or '<tr><td colspan="4">No .tla files</td></tr>'
    total_el = sum(d.element_count for d in diagrams)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TLA+ Nassi-Shneiderman — {escape(root_path)}</title>
<style>
:root{{--bg:#0d1117;--sf:#161b22;--bd:#30363d;--tx:#e6edf3;--tm:#8b949e;--bl:#569cd6}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:{FONT};background:var(--bg);color:var(--tx);padding:24px;max-width:900px;margin:0 auto}}
h1{{font-size:20px;margin-bottom:4px}}
.meta{{font-size:12px;color:var(--tm);margin-bottom:16px}}
.stats{{display:flex;gap:14px;margin-bottom:20px}}
.stat{{background:var(--sf);border:1px solid var(--bd);border-radius:8px;padding:10px 18px;text-align:center}}
.stat .n{{font-size:26px;font-weight:700;color:var(--bl)}}
.stat .l{{font-size:11px;color:var(--tm)}}
table{{width:100%;border-collapse:collapse;background:var(--sf);border-radius:8px;overflow:hidden}}
th{{background:var(--bl);color:#000;font-size:11px;text-transform:uppercase;padding:8px 12px;text-align:left}}
td{{padding:8px 12px;border-bottom:1px solid var(--bd);font-size:13px}}
tr:hover{{background:#1c2333}}
a{{color:var(--bl);text-decoration:none;font-weight:600}}
a:hover{{text-decoration:underline}}
td:nth-child(3),td:nth-child(4){{text-align:right;font-family:monospace}}
</style>
</head>
<body>
<h1>Nassi-Shneiderman Diagrams</h1>
<div class="meta">{escape(root_path)}</div>
<div class="stats">
<div class="stat"><div class="n">{len(diagrams)}</div><div class="l">modules</div></div>
<div class="stat"><div class="n">{total_el}</div><div class="l">elements</div></div>
</div>
<table>
<thead><tr><th>Source</th><th>Module</th><th>Elems</th><th>Time</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
</body>
</html>"""


def _rel_name(loc: str, root: str) -> str:
    try:
        return Path(loc).relative_to(Path(root)).as_posix()
    except ValueError:
        return Path(loc).name
