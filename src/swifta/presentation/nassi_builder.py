"""Build Nassi-Shneiderman diagrams from TLA+ AST."""

from __future__ import annotations

from swifta.presentation.nassi_blocks import ActionBlock, Block


class NassiBuilder:
    """Converts TLA+ expression AST into NSD block tree.

    This is a placeholder implementation. Full version requires mapping ANTLR contexts
    to structural blocks by analyzing their structure.
    """

    def build(self, expr_ctx) -> Block:
        """Build NSD block from expression context."""
        # TODO: Implement AST traversal
        # For now, return a simple action block representing the expression text.
        text = expr_ctx.getText().strip() if hasattr(expr_ctx, "getText") else str(expr_ctx)
        return ActionBlock(text=text[:120])
