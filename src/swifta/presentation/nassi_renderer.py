"""Render Nassi-Shneiderman blocks to SVG.

Implements a proper NSD visual style:
  - IF: triangle header with condition text, THEN/ELSE branches side by side
  - CASE: header row + stacked arm rows
  - Sequence: blocks stacked vertically with minimal indent
  - Scope (LET): labeled header
  - Action: colored by kind (state, predicate, expression)
"""

from __future__ import annotations

from swifta.presentation.nassi_blocks import (
    Block,
    ActionBlock,
    SequenceBlock,
    SelectionBlock,
    CaseBlock,
    ScopeBlock,
    EmptyBlock,
)

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
DIAGRAM_W = 800
MX = 20  # horizontal margin
MY = 16  # top margin after title
BH = 30  # block height
BP = 4  # padding between blocks
INDENT = 16  # indent per nesting level
COND_H = 32  # IF condition triangle height

# ---------------------------------------------------------------------------
# Colour palette (dark theme)
# ---------------------------------------------------------------------------
BG = "#0d1117"
C_ACTION = "#161b22"
C_ACTION_ST = "#30363d"
C_COND_BG = "#1a2233"
C_COND_ST = "#58a6ff"
C_CASE_BG = "#1c1e2e"
C_CASE_ST = "#bc8cff"
C_SCOPE_BG = "#1a2744"
C_SCOPE_ST = "#d2a8ff"
C_TEXT = "#e6edf3"
C_TEXT_DIM = "#8b949e"
C_THEN = "#3fb950"
C_ELSE = "#f85149"
C_ARM = "#bc8cff"
C_COND_TEXT = "#58a6ff"

# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """Escape HTML entities in text for SVG."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _fit_text(text: str, max_chars: int = 80) -> str:
    t = text.strip()
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 1] + "…"


def _svg_block(x: float, y: float, w: float, h: float, fill: str, stroke: str,
               text: str, text_color: str = C_TEXT, font_size: int = 12,
               font_weight: str = "normal", text_anchor: str = "middle",
               text_x: float | None = None, rx: int = 4) -> str:
    """Rounded rect with text."""
    tx = text_x if text_x is not None else x + w / 2
    ty = y + h / 2 + font_size * 0.35
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        f'<text x="{tx}" y="{ty}" text-anchor="{text_anchor}" fill="{text_color}" '
        f'font-family="JetBrains Mono,Fira Code,monospace" font-size="{font_size}" '
        f'font-weight="{font_weight}">{_esc(_fit_text(text))}</text>'
    )


def _svg_triangle(x: float, y: float, w: float, h: float, fill: str, stroke: str,
                  cond_text: str) -> str:
    """Draw NSD IF triangle with condition text."""
    mid_x = x + w / 2
    # Triangle points: top-left, top-right, bottom-center
    pts = f"{x},{y} {x + w},{y} {mid_x},{y + h}"
    return (
        f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        # Condition text centered in upper portion of triangle
        f'<text x="{mid_x}" y="{y + h * 0.45}" text-anchor="middle" fill="{C_COND_TEXT}" '
        f'font-family="JetBrains Mono,Fira Code,monospace" font-size="11" '
        f'font-weight="bold">{_esc(_fit_text(cond_text, 50))}</text>'
        # THEN label (left)
        f'<text x="{x + 20}" y="{y + h * 0.8}" text-anchor="start" fill="{C_THEN}" '
        f'font-family="JetBrains Mono,monospace" font-size="9" font-weight="bold">T</text>'
        # ELSE label (right)
        f'<text x="{x + w - 20}" y="{y + h * 0.8}" text-anchor="end" fill="{C_ELSE}" '
        f'font-family="JetBrains Mono,monospace" font-size="9" font-weight="bold">F</text>'
    )


def _svg_divider(y: float, x1: float, x2: float, label: str = "", color: str = C_TEXT_DIM) -> str:
    """Thin divider line with optional label."""
    parts = [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="0.5" opacity="0.5"/>']
    if label:
        parts.append(
            f'<text x="{x1 + 4}" y="{y - 2}" fill="{color}" '
            f'font-family="JetBrains Mono,monospace" font-size="9" opacity="0.7">{label}</text>'
        )
    return "".join(parts)


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render_nassi_diagram(root: Block, op_name: str, variant: str = "seq") -> str:
    """Render NSD block tree to SVG string."""
    parts: list[str] = []
    y = MY

    # --- Measure pass (compute total height) ---
    # We do a two-pass approach: first measure, then draw.
    # For simplicity we draw in one pass and compute height at the end.

    def draw(block: Block, x: float, y: float, w: float, depth: int = 0) -> float:
        """Draw a block. Returns new y position."""

        if isinstance(block, EmptyBlock):
            return y

        # --- Sequence ---
        if isinstance(block, SequenceBlock):
            cy = y
            for child in block.children:
                cy = draw(child, x, cy, w, depth)
            return cy

        # --- IF / Selection ---
        if isinstance(block, SelectionBlock):
            return _draw_selection(block, x, y, w, depth, parts)

        # --- CASE ---
        if isinstance(block, CaseBlock):
            return _draw_case(block, x, y, w, depth, parts)

        # --- Scope (LET...IN) ---
        if isinstance(block, ScopeBlock):
            return _draw_scope(block, x, y, w, depth, parts)

        # --- Action (leaf) ---
        if isinstance(block, ActionBlock):
            text = block.text or block.label or "—"
            fill, stroke = _action_colors(text)
            parts.append(_svg_block(x, y, w, BH, fill, stroke, text))
            return y + BH + BP

        # --- Fallback ---
        text = getattr(block, "text", None) or block.label or block.kind
        parts.append(_svg_block(x, y, w, BH, C_ACTION, C_ACTION_ST, text))
        return y + BH + BP

    total_y = draw(root, MX, y, DIAGRAM_W - 2 * MX)
    total_h = total_y + MY

    # Assemble SVG
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{DIAGRAM_W}" height="{total_h}" '
        f'viewBox="0 0 {DIAGRAM_W} {total_h}">\n'
        f'<rect width="100%" height="100%" fill="{BG}" rx="8"/>\n'
    )
    svg += "\n".join(parts)
    svg += "\n</svg>"
    return svg


# ---------------------------------------------------------------------------
# Selection (IF/THEN/ELSE)
# ---------------------------------------------------------------------------

def _draw_selection(block: SelectionBlock, x: float, y: float, w: float,
                    depth: int, parts: list[str]) -> float:
    cond = block.condition or "?"
    then_br = block.then_branch
    else_br = block.else_branch

    # 1. Draw triangle header
    parts.append(_svg_triangle(x, y, w, COND_H, C_COND_BG, C_COND_ST, cond))
    y += COND_H + BP

    # 2. THEN branch — full width
    if then_br and not isinstance(then_br, EmptyBlock):
        y = draw_block(then_br, x, y, w, depth + 1, parts)

    # 3. ELSE branch — full width, with divider
    if else_br and not isinstance(else_br, EmptyBlock):
        parts.append(_svg_divider(y, x, x + w, "ELSE", C_ELSE))
        y += BP * 2
        y = draw_block(else_br, x, y, w, depth + 1, parts)

    return y


def draw_block(block: Block, x: float, y: float, w: float,
               depth: int, parts: list[str]) -> float:
    """Dispatch block drawing (module-level helper for recursion)."""
    if isinstance(block, EmptyBlock):
        return y
    if isinstance(block, SequenceBlock):
        cy = y
        for child in block.children:
            cy = draw_block(child, x, cy, w, depth)
        return cy
    if isinstance(block, SelectionBlock):
        return _draw_selection(block, x, y, w, depth, parts)
    if isinstance(block, CaseBlock):
        return _draw_case(block, x, y, w, depth, parts)
    if isinstance(block, ScopeBlock):
        return _draw_scope(block, x, y, w, depth, parts)
    if isinstance(block, ActionBlock):
        text = block.text or block.label or "—"
        fill, stroke = _action_colors(text)
        parts.append(_svg_block(x, y, w, BH, fill, stroke, text))
        return y + BH + BP
    # fallback
    text = getattr(block, "text", None) or block.label or block.kind
    parts.append(_svg_block(x, y, w, BH, C_ACTION, C_ACTION_ST, text))
    return y + BH + BP


# ---------------------------------------------------------------------------
# CASE
# ---------------------------------------------------------------------------

def _draw_case(block: CaseBlock, x: float, y: float, w: float,
               depth: int, parts: list[str]) -> float:
    # Header
    parts.append(_svg_block(x, y, w, BH, C_CASE_BG, C_CASE_ST, "CASE",
                            C_CASE_ST, font_weight="bold"))
    y += BH + BP

    for idx, (pattern, body) in enumerate(block.arms):
        # Arm label row
        arm_label = f"▸ {pattern}"
        parts.append(_svg_block(x, y, w, BH, C_CASE_BG, C_CASE_ST, arm_label,
                                C_ARM, font_size=11))
        y += BH + BP

        # Body (indented)
        if body and not isinstance(body, EmptyBlock):
            ix = x + INDENT
            iw = w - INDENT
            y = draw_block(body, ix, y, iw, depth + 1, parts)

    return y


# ---------------------------------------------------------------------------
# Scope (LET...IN)
# ---------------------------------------------------------------------------

def _draw_scope(block: ScopeBlock, x: float, y: float, w: float,
                depth: int, parts: list[str]) -> float:
    label = block.label or "SCOPE"
    parts.append(_svg_block(x, y, w, BH, C_SCOPE_BG, C_SCOPE_ST, label,
                            C_SCOPE_ST, font_weight="bold", rx=6))
    y += BH + BP

    for child in block.children:
        y = draw_block(child, x + INDENT, y, w - INDENT, depth + 1, parts)
    return y


# ---------------------------------------------------------------------------
# Action colour coding
# ---------------------------------------------------------------------------

def _action_colors(text: str) -> tuple[str, str]:
    """Pick fill/stroke based on action semantics."""
    t = text.strip()
    # Primed variable (state transition)
    if "'" in t:
        return "#0d1f0d", "#3fb950"  # green tint
    # Temporal ([] <>, ~>)
    if t.startswith("[]") or t.startswith("<>") or t.startswith("~[]"):
        return "#1f1a0d", "#d29922"  # amber tint
    # String literal
    if t.startswith('"'):
        return "#1a1533", "#bc8cff"  # purple tint
    # Negation
    if t.startswith("~") or t.startswith("\\") and "lnot" in t[:8]:
        return "#1f130d", "#f0883e"  # orange tint
    # Default
    return C_ACTION, C_ACTION_ST
