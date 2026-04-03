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
C_DIVIDER = "#30363d"

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


def _svg_divider_v(x: float, y1: float, y2: float, color: str = C_COND_ST) -> str:
    """Vertical divider line (for IF side-by-side branches)."""
    return (
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" '
        f'stroke="{color}" stroke-width="1.5" opacity="0.6"/>'
    )


def _svg_padding(x: float, y: float, w: float, h: float) -> str:
    """Empty padding rect to equalise branch heights."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'fill="{C_ACTION}" stroke="{C_DIVIDER}" stroke-width="0.5" opacity="0.15"/>'
    )


# ---------------------------------------------------------------------------
# Height measurement (no rendering)
# ---------------------------------------------------------------------------

def _measure(block: Block | None, w: float) -> float:
    """Compute the pixel height needed to render *block* at width *w*."""
    if block is None or isinstance(block, EmptyBlock):
        return 0

    if isinstance(block, ActionBlock):
        return BH + BP

    if isinstance(block, SequenceBlock):
        total = 0.0
        for child in block.children:
            total += _measure(child, w)
        return total

    if isinstance(block, SelectionBlock):
        half = w / 2
        h = COND_H + BP
        then_h = _measure(block.then_branch, half)
        else_h = _measure(block.else_branch, half)
        h += max(then_h, else_h)
        return h

    if isinstance(block, CaseBlock):
        h = BH + BP  # header
        for _, body in block.arms:
            h += BH + BP  # arm label row
            h += _measure(body, w - INDENT)
        return h

    if isinstance(block, ScopeBlock):
        h = BH + BP  # header
        for child in block.children:
            h += _measure(child, w - INDENT)
        return h

    return BH + BP


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render_nassi_diagram(root: Block, op_name: str, variant: str = "seq") -> str:
    """Render NSD block tree to SVG string."""
    parts: list[str] = []
    y = MY

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
# Selection (IF/THEN/ELSE) — side-by-side NSD layout
# ---------------------------------------------------------------------------

def _draw_selection(block: SelectionBlock, x: float, y: float, w: float,
                    depth: int, parts: list[str]) -> float:
    cond = block.condition or "?"
    then_br = block.then_branch
    else_br = block.else_branch

    half_w = w / 2

    # Measure branch heights
    then_h = _measure(then_br, half_w) if then_br and not isinstance(then_br, EmptyBlock) else 0
    else_h = _measure(else_br, half_w) if else_br and not isinstance(else_br, EmptyBlock) else 0
    max_h = max(then_h, else_h)

    # 1. Draw triangle header (full width)
    parts.append(_svg_triangle(x, y, w, COND_H, C_COND_BG, C_COND_ST, cond))
    y += COND_H + BP
    branch_top = y

    # 2. Draw THEN branch (left half)
    then_used = 0.0
    if then_br and not isinstance(then_br, EmptyBlock):
        then_used = draw_block(then_br, x, y, half_w, depth + 1, parts)

    # 3. Padding for THEN if shorter
    if then_h < max_h:
        parts.append(_svg_padding(x, y + then_h, half_w, max_h - then_h))

    # 4. Draw ELSE branch (right half)
    else_used = 0.0
    if else_br and not isinstance(else_br, EmptyBlock):
        else_used = draw_block(else_br, x + half_w, y, half_w, depth + 1, parts)

    # 5. Padding for ELSE if shorter
    if else_h < max_h:
        parts.append(_svg_padding(x + half_w, y + else_h, half_w, max_h - else_h))

    # 6. Vertical divider between branches
    parts.append(_svg_divider_v(x + half_w, branch_top, branch_top + max_h))

    return y + max_h


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
