"""Render Nassi-Shneiderman blocks to SVG."""

from __future__ import annotations

from typing import List

from swifta.presentation.nassi_blocks import (
    Block,
    ActionBlock,
    SequenceBlock,
    SelectionBlock,
    CaseBlock,
    ScopeBlock,
)

# Constants (reuse from tlaplus_structure_renderer or define locally)
DIAGRAM_W = 800
MARGIN_X = 30
MARGIN_Y = 20
BLOCK_H = 28
BLOCK_PAD = 6
INDENT_STEP = 20

C_BG = "#0d1117"
C_BLOCK = "#1e2533"
C_BLOCK_STROKE = "#3b4660"
C_TEXT = "#d4d4d4"
C_TEXT_DIM = "#808080"


def _svg_rect(
    x: int,
    y: int,
    w: int,
    h: int,
    fill: str,
    stroke: str,
    text: str,
    text_color: str = C_TEXT,
    radius: int = 0,
    font_weight: str = "normal",
    sub: str = "",
) -> str:
    """Return SVG rect with centered text."""
    label = f"{text} {sub}".strip()
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" ry="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 4}" text-anchor="middle" fill="{text_color}" font-family="JetBrains Mono, Fira Code, monospace" font-size="12" font-weight="{font_weight}">{label}</text>'
    )


def _draw_condition_line(y: int, text: str, x: int, w: int) -> str:
    """Draw a thin dashed line with condition label."""
    line_y = y + BLOCK_PAD // 2
    return (
        f'<line x1="{x}" y1="{line_y}" x2="{x + w}" y2="{line_y}" stroke="{C_TEXT_DIM}" stroke-dasharray="2,2" stroke-width="1"/>'
        f'<text x="{x + 5}" y="{line_y - 2}" fill="{C_TEXT_DIM}" font-family="JetBrains Mono, monospace" font-size="10">{text}</text>'
    )


def render_nassi_diagram(root: Block, module_name: str, variant: str = "seq") -> str:
    """
    Render NSD tree to SVG string.

    Args:
        root: Root Block of the NSD tree
        module_name: Name of the TLA+ module
        variant: "seq" (sequence) or "if" (if-style) – controls layout

    Returns:
        SVG string
    """
    # width used implicitly in _svg_rect, no need to track separately
    drawn_parts: List[str] = []
    y_cursor = 0

    # Title
    drawn_parts.append(
        f'<text x="{MARGIN_X}" y="24" fill="{C_TEXT}" font-family="JetBrains Mono, monospace" font-size="14" font-weight="bold">NSD: {module_name}</text>'
    )
    y_cursor = 35

    def draw_block(block: Block, x: int, y: int, width: int, indent: int = 0) -> int:
        """Recursively draw block and children. Returns new y."""
        if isinstance(block, ActionBlock):
            text = block.text if block.text else block.label
            drawn_parts.append(
                _svg_rect(x, y, width, BLOCK_H, C_BLOCK, C_BLOCK_STROKE, text, C_TEXT, 0, "normal")
            )
            return y + BLOCK_H + BLOCK_PAD
        elif isinstance(block, SequenceBlock):
            # Draw children stacked, with reduced width for indentation
            current_y = y
            for child in block.children:
                child_x = x + INDENT_STEP
                child_w = width - 2 * INDENT_STEP
                if child_w < 100:
                    child_w = width - INDENT_STEP
                    child_x = x + INDENT_STEP // 2
                current_y = draw_block(child, child_x, current_y, child_w, indent + 1)
            return current_y
        elif isinstance(block, SelectionBlock):
            # THEN branch
            y1 = y + BLOCK_H + BLOCK_PAD
            # THEN
            drawn_parts.append(_draw_condition_line(y1, "THEN", x, width))
            y2 = y1 + BLOCK_PAD
            y2 = draw_block(
                block.then_branch, x + INDENT_STEP, y2, width - 2 * INDENT_STEP, indent + 1
            )
            # ELSE if exists
            if block.else_branch:
                y3 = y2 + BLOCK_PAD
                drawn_parts.append(_draw_condition_line(y3, "ELSE", x, width))
                y4 = y3 + BLOCK_PAD
                y4 = draw_block(
                    block.else_branch, x + INDENT_STEP, y4, width - 2 * INDENT_STEP, indent + 1
                )
                return y4
            return y2
        elif isinstance(block, CaseBlock):
            # CASE label
            drawn_parts.append(
                _svg_rect(x, y, width, BLOCK_H, C_BLOCK, C_BLOCK_STROKE, "CASE", C_TEXT, 0, "bold")
            )
            y_cur = y + BLOCK_H + BLOCK_PAD
            for idx, (pat, body) in enumerate(block.arms):
                pat_label = f"• {pat}"
                drawn_parts.append(
                    _svg_rect(
                        x,
                        y_cur,
                        width,
                        BLOCK_H,
                        C_BLOCK,
                        C_BLOCK_STROKE,
                        pat_label,
                        C_TEXT,
                        0,
                        "normal",
                    )
                )
                y_body = y_cur + BLOCK_H + BLOCK_PAD
                y_cur = draw_block(
                    body, x + INDENT_STEP, y_body, width - 2 * INDENT_STEP, indent + 1
                )
            return y_cur
        elif isinstance(block, ScopeBlock):
            drawn_parts.append(
                _svg_rect(
                    x, y, width, BLOCK_H, "#1a2744", C_BLOCK_STROKE,
                    block.label or "SCOPE", C_TEXT, 0, "bold",
                )
            )
            y_cur = y + BLOCK_H + BLOCK_PAD
            for child in block.children:
                y_cur = draw_block(child, x + INDENT_STEP, y_cur, width - 2 * INDENT_STEP, indent + 1)
            return y_cur
        else:
            # Unknown block type – render as text
            drawn_parts.append(
                _svg_rect(
                    x,
                    y,
                    width,
                    BLOCK_H,
                    C_BLOCK,
                    C_BLOCK_STROKE,
                    block.label or str(block.kind),
                    C_TEXT,
                    0,
                    "normal",
                )
            )
            return y + BLOCK_H + BLOCK_PAD

    total_y = draw_block(root, MARGIN_X, y_cursor, DIAGRAM_W - 2 * MARGIN_X)
    total_h = total_y + MARGIN_Y

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
