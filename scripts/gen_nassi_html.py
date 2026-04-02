#!/usr/bin/env python3
"""
Generate Nassi-Shneiderman-style HTML structure diagrams for TLA+ modules.

Usage:
    python scripts/gen_nassi_html.py tests/fixtures/valid.tla
    python scripts/gen_nassi_html.py tests/fixtures/valid.tla --out diagram.html
"""

from __future__ import annotations

import argparse
import sys
from html import escape
from pathlib import Path
from time import perf_counter

# Ensure src/ is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from swifta.infrastructure.antlr.parser_adapter import AntlrTlaplusSyntaxParser
from swifta.infrastructure.antlr.runtime import load_generated_types, parse_source_text
from swifta.domain.model import SourceUnit, SourceUnitId


def _depth_badge(i: int) -> str:
    if i <= 0:
        return ""
    if i <= 20:
        return f" {chr(0x2460 + i - 1)}"
    if i <= 35:
        return f" {chr(0x3251 + i - 21)}"
    return f" {chr(0x32B1 + i - 36)}"


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
    "module": "📦",
    "extends": "🔗",
    "variable": "x",
    "constant": "C",
    "operator_definition": "≜",
    "function_definition": "↦",
    "module_definition": "⊞",
    "recursive": "↺",
    "instance": "⇒",
    "assumption": "assume",
    "theorem": "theorem",
    "proof": "proof",
    "use": "use",
    "hide": "hide",
}


def _render_element_block(element, depth: int) -> str:
    kind = element.kind
    palette = _KIND_COLORS.get(kind, ("gray", "#7f8c8d", "#616a6b"))
    color_name, bg, border = palette
    icon = _KIND_ICONS.get(kind, "•")
    badge = _depth_badge(depth)
    sig = escape(element.signature) if element.signature else ""
    name = escape(element.name)
    container = escape(element.container) if element.container else ""

    label_parts = []
    if icon and len(icon) <= 2:
        label_parts.append(f'<span class="icon">{icon}</span>')
    label_parts.append(f'<span class="name">{name}</span>')
    if badge:
        label_parts.append(f'<span class="badge">{badge}</span>')

    meta_parts = []
    if sig:
        meta_parts.append(f"<code>{sig}</code>")
    if container:
        meta_parts.append(f'<span class="container">in {container}</span>')
    meta_parts.append(f'<span class="loc">L{element.line}</span>')

    return f"""      <div class="block block-{color_name}" style="border-left: 4px solid {border};">
        <div class="block-header" style="background: {bg}22;">
          {"".join(label_parts)}
          <span class="kind-tag" style="background: {bg};">{escape(kind)}</span>
        </div>
        <div class="block-meta">{"".join(meta_parts)}</div>
      </div>"""


def render_html(
    source_path: str,
    elements: list,
    diagnostics: list,
    elapsed_ms: float,
    token_count: int,
) -> str:
    module_name = "TLA+ Module"
    for elem in elements:
        if elem.kind == "module":
            module_name = elem.name
            break

    # Group elements by kind for the summary
    kind_counts: dict[str, int] = {}
    for elem in elements:
        kind_counts[elem.kind] = kind_counts.get(elem.kind, 0) + 1

    summary_items = "".join(
        f'<span class="summary-chip" style="background: {_KIND_COLORS.get(k, ("gray", "#7f8c8d", "#616a6b"))[1]}33; '
        f'border-color: {_KIND_COLORS.get(k, ("gray", "#7f8c8d", "#616a6b"))[1]};">'
        f"{v} {escape(k.replace('_', ' '))}</span>"
        for k, v in sorted(kind_counts.items())
    )

    diag_html = ""
    if diagnostics:
        diag_rows = "".join(
            f'<tr><td class="diag-sev">{"ERROR" if d.severity.value == "error" else "WARN"}</td>'
            f"<td>L{d.line}:{d.column}</td><td>{escape(d.message)}</td></tr>"
            for d in diagnostics
        )
        diag_html = f"""
      <details class="diagnostics">
        <summary>{len(diagnostics)} diagnostic(s)</summary>
        <table><thead><tr><th>Severity</th><th>Location</th><th>Message</th></tr></thead>
        <tbody>{diag_rows}</tbody></table>
      </details>"""

    # Build blocks
    depth = 0
    blocks_html = []
    for elem in elements:
        if elem.kind == "module":
            depth = 0
        elif elem.kind in ("operator_definition", "function_definition", "module_definition"):
            depth = 1
        elif elem.kind in ("theorem", "assumption", "proof"):
            depth = 2
        else:
            depth = 1
        blocks_html.append(_render_element_block(elem, depth))

    if not blocks_html:
        blocks_html.append(
            '<div class="block block-gray"><div class="block-header">No structural elements found</div></div>'
        )

    body = "\n".join(blocks_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TLA+ Structure — {escape(module_name)}</title>
  <style>
    :root {{
      --bg: #0d1117;
      --surface: #161b22;
      --surface-2: #21262d;
      --border: #30363d;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --blue: #1676dc;
      --green: #2d9d4a;
      --purple: #9b59b6;
      --teal: #1abc9c;
      --amber: #f39c12;
      --red: #e74c3c;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "IBM Plex Sans", -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 24px;
      max-width: 960px;
      margin: 0 auto;
    }}
    .header {{
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }}
    .header h1 {{
      font-size: 22px;
      font-weight: 600;
      margin-bottom: 6px;
    }}
    .header .meta {{
      font-size: 13px;
      color: var(--text-muted);
      font-family: "JetBrains Mono", monospace;
    }}
    .summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 20px;
    }}
    .summary-chip {{
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      border: 1px solid;
    }}
    .diagnostics {{
      margin-bottom: 20px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
    }}
    .diagnostics summary {{
      cursor: pointer;
      color: var(--red);
      font-weight: 500;
      margin-bottom: 8px;
    }}
    .diagnostics table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    .diagnostics th, .diagnostics td {{
      text-align: left;
      padding: 6px 10px;
      border-bottom: 1px solid var(--border);
    }}
    .diag-sev {{
      color: var(--red);
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
    }}
    .structure {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .block {{
      background: var(--surface);
      border-radius: 6px;
      overflow: hidden;
      transition: transform 0.1s;
    }}
    .block:hover {{
      transform: translateX(2px);
    }}
    .block-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      font-size: 14px;
      font-weight: 500;
    }}
    .block-header .icon {{
      font-size: 16px;
      width: 22px;
      text-align: center;
    }}
    .block-header .name {{
      font-family: "JetBrains Mono", monospace;
      font-weight: 600;
      font-size: 14px;
    }}
    .block-header .badge {{
      color: var(--text-muted);
      font-size: 14px;
    }}
    .block-header .kind-tag {{
      margin-left: auto;
      padding: 2px 8px;
      border-radius: 8px;
      font-size: 10px;
      font-weight: 600;
      color: #fff;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .block-meta {{
      padding: 4px 14px 8px 44px;
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .block-meta code {{
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      color: var(--text);
      background: var(--surface-2);
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .block-meta .container {{
      font-style: italic;
    }}
    .block-meta .loc {{
      font-family: "JetBrains Mono", monospace;
      font-size: 11px;
    }}
    .source-preview {{
      margin-top: 24px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }}
    .source-preview summary {{
      padding: 10px 14px;
      cursor: pointer;
      font-weight: 500;
      color: var(--text-muted);
    }}
    .source-preview pre {{
      padding: 14px;
      font-family: "JetBrains Mono", monospace;
      font-size: 13px;
      line-height: 1.5;
      overflow-x: auto;
      border-top: 1px solid var(--border);
      max-height: 600px;
      overflow-y: auto;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{escape(module_name)}</h1>
    <div class="meta">{escape(source_path)} &middot; {token_count} tokens &middot; {elapsed_ms:.1f}ms</div>
  </div>

  <div class="summary">{summary_items}</div>

  {diag_html}

  <div class="structure">
{body}
  </div>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate TLA+ structure diagram HTML.")
    parser.add_argument("path", help="Path to a .tla file.")
    parser.add_argument("--out", "-o", help="Output HTML path. Default: <input>.structure.html")
    args = parser.parse_args()

    source_path = Path(args.path).expanduser().resolve()
    if not source_path.exists():
        print(f"Error: file not found: {source_path}", file=sys.stderr)
        return 1

    content = source_path.read_text(encoding="utf-8")
    generated = load_generated_types()

    t0 = perf_counter()
    result = parse_source_text(content, generated)
    elapsed_ms = round((perf_counter() - t0) * 1000, 3)

    # Extract structural elements
    visitor_base = generated.visitor_type

    class QuickVisitor(visitor_base):
        def __init__(self):
            super().__init__()
            self.elements = []
            self._module_name = None

        def visitFirstModule(self, ctx):
            if ctx.IDENTIFIER():
                self._module_name = ctx.IDENTIFIER().getText()
                self._add("module", self._module_name, ctx)
            body = ctx.moduleBody()
            if body:
                for child in body.getChildren():
                    self.visit(child)
            return None

        def visitModule(self, ctx):
            if ctx.IDENTIFIER():
                self._module_name = ctx.IDENTIFIER().getText()
                self._add("module", self._module_name, ctx)
            body = ctx.moduleBody()
            if body:
                for child in body.getChildren():
                    self.visit(child)
            return None

        def visitExtends(self, ctx):
            for ident in ctx.IDENTIFIER():
                self._add("extends", ident.getText(), ctx)
            return None

        def visitVariableDeclaration(self, ctx):
            for ident in ctx.IDENTIFIER():
                self._add("variable", ident.getText(), ctx, f"VARIABLE {ident.getText()}")
            return None

        def visitParameterDeclaration(self, ctx):
            for item in ctx.constantDeclItem():
                name = item.IDENTIFIER().getText() if item.IDENTIFIER() else item.getText()
                self._add("constant", name, ctx, f"CONSTANT {name}")
            return None

        def visitRecursiveDeclaration(self, ctx):
            for item in ctx.constantDeclItem():
                name = item.IDENTIFIER().getText() if item.IDENTIFIER() else item.getText()
                self._add("recursive", name, ctx, f"RECURSIVE {name}")
            return None

        def visitOperatorDefinition(self, ctx):
            lhs = ctx.identLhs()
            name = lhs.IDENTIFIER().getText() if lhs and lhs.IDENTIFIER() else "?"
            self._add("operator_definition", name, ctx, f"{name} == ...")
            return None

        def visitFunctionDefinition(self, ctx):
            name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else "?"
            self._add("function_definition", name, ctx, f"{name}[...] == ...")
            return None

        def visitModuleDefinition(self, ctx):
            name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else "?"
            self._add("module_definition", name, ctx, f"{name} == ...")
            return None

        def visitInstance(self, ctx):
            inst = ctx.instantiation()
            if inst and inst.IDENTIFIER():
                self._add("instance", inst.IDENTIFIER().getText(), ctx)
            return None

        def visitAssumption(self, ctx):
            name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else "ASSUME"
            self._add("assumption", name, ctx)
            return None

        def visitTheorem(self, ctx):
            name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else "THEOREM"
            self._add("theorem", name, ctx, f"THEOREM {name}" if ctx.IDENTIFIER() else "THEOREM")
            return self.visitChildren(ctx)

        def visitProof(self, ctx):
            self._add("proof", "PROOF", ctx)
            return self.visitChildren(ctx)

        def _add(self, kind, name, ctx, sig=None):
            line = ctx.start.line if ctx.start else 0
            col = ctx.start.column if ctx.start else 0
            from swifta.domain.model import StructuralElement, StructuralElementKind

            try:
                k = StructuralElementKind(kind)
            except ValueError:
                k = kind
            self.elements.append(
                StructuralElement(
                    kind=k,
                    name=name,
                    line=line,
                    column=col,
                    container=self._module_name,
                    signature=sig,
                )
            )

    visitor = QuickVisitor()
    visitor.visit(result.tree)

    html = render_html(
        source_path=str(source_path),
        elements=visitor.elements,
        diagnostics=list(result.diagnostics),
        elapsed_ms=elapsed_ms,
        token_count=len(result.token_stream.tokens),
    )

    out_path = Path(args.out) if args.out else source_path.with_suffix(".structure.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"Generated: {out_path}")
    print(f"  {len(visitor.elements)} structural elements")
    print(f"  {len(result.diagnostics)} diagnostics")
    print(f"  {elapsed_ms:.1f}ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
