"""Build Nassi-Shneiderman diagrams from TLA+ AST."""

from __future__ import annotations

from swifta.presentation.nassi_blocks import (
    ActionBlock,
    Block,
    CaseBlock,
    EmptyBlock,
    ScopeBlock,
    SelectionBlock,
    SequenceBlock,
)

_MAX_TEXT = 120


def _truncate(text: str, limit: int = _MAX_TEXT) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


class NassiBuilder:
    """Converts TLA+ expression AST contexts into NSD block trees."""

    def __init__(self) -> None:
        self._parser_cls: type | None = None

    def _ensure_parser_cls(self) -> type:
        if self._parser_cls is None:
            from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParser import (
                TLAPLusParser,
            )

            self._parser_cls = TLAPLusParser
        return self._parser_cls

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_all_operators(self, content: str) -> list[tuple[str, Block, int]]:
        """Parse *content* and build an NSD block tree for every operator definition.

        Returns a list of ``(operator_name, block_tree, line_number)``.
        """
        from swifta.infrastructure.antlr.parser_adapter import _build_structure_visitor
        from swifta.infrastructure.antlr.runtime import load_generated_types, parse_source_text
        from swifta.domain.model import StructuralElementKind

        generated = load_generated_types()
        result = parse_source_text(content, generated)

        visitor_cls = _build_structure_visitor(generated.visitor_type)
        visitor = visitor_cls()
        visitor.visit(result.tree)

        diagrams: list[tuple[str, Block, int]] = []
        for elem in visitor.elements:
            if elem.kind == StructuralElementKind.OPERATOR_DEFINITION:
                ctx = visitor.get_context(elem)
                if ctx is not None and hasattr(ctx, "expression"):
                    block = self.build_from_expression(ctx.expression())
                    diagrams.append((elem.name, block, elem.line))

        return diagrams

    def build_from_expression(self, expr_ctx) -> Block:
        """Build NSD block from an ANTLR *expression* context."""
        return self._build_expr(expr_ctx)

    # ------------------------------------------------------------------
    # Recursive dispatch
    # ------------------------------------------------------------------

    def _build_expr(self, ctx) -> Block:  # noqa: C901 – unavoidable complexity
        P = self._ensure_parser_cls()

        if ctx is None:
            return EmptyBlock()

        # ---- Structural constructs (check subclasses BEFORE parent types) ----

        # IF cond THEN a ELSE b
        if isinstance(ctx, P.IfThenElseExpressionContext):
            return self._build_if(ctx)

        # CASE pat -> e [] pat -> e [] OTHER -> e
        if isinstance(ctx, P.CaseExpressionContext):
            return self._build_case(ctx)

        # LET def+ IN expr
        if isinstance(ctx, P.LetInExpressionContext):
            return self._build_let(ctx)

        # /\ expr /\ expr ...
        if isinstance(ctx, P.ConjunctionListContext):
            return self._build_conjunction_list(ctx)

        # \/ expr \/ expr ...
        if isinstance(ctx, P.DisjunctionListContext):
            return self._build_disjunction_list(ctx)

        # a /\ b  (binary conjunction)
        if isinstance(ctx, P.AndBinaryExprContext):
            return self._build_and_binary(ctx)

        # a \/ b  (binary disjunction)
        if isinstance(ctx, P.OrBinaryExprContext):
            return self._build_or_binary(ctx)

        # Inline /\ and \/ at the addExpr level (AND, LAND, OR, LOR tokens)
        if isinstance(ctx, P.AddBinaryExprContext):
            return self._build_add_binary(ctx)

        # ---- Quantifier expressions → leaf for now ----
        if isinstance(ctx, (P.QuantifierExpressionContext, P.TemporalQuantifierExpressionContext)):
            return ActionBlock(text=_truncate(ctx.getText()))
        if isinstance(ctx, P.ChooseExpressionContext):
            return ActionBlock(text=_truncate(ctx.getText()))

        # ---- Pass-through unwrapping ----
        unwrapped = self._unwrap(ctx)
        if unwrapped is not None:
            return self._build_expr(unwrapped)

        # ---- Leaf ----
        return ActionBlock(text=_truncate(ctx.getText()))

    # ------------------------------------------------------------------
    # Pass-through unwrapping
    # ------------------------------------------------------------------

    def _unwrap(self, ctx):
        """Unwrap one pass-through layer.  Returns inner context or ``None``."""
        P = self._ensure_parser_cls()

        # Level 0: Expression → quantifierExpr
        if isinstance(ctx, P.ExpressionContext):
            return ctx.quantifierExpr()

        # Level 1
        if isinstance(ctx, P.QuantifierPassThroughContext):
            return ctx.chooseExpr()

        # Level 2
        if isinstance(ctx, P.ChoosePassThroughContext):
            return ctx.ifExpr()

        # Level 3
        if isinstance(ctx, P.IfPassThroughContext):
            return ctx.caseExpr()

        # Level 4
        if isinstance(ctx, P.CasePassThroughContext):
            return ctx.letExpr()

        # Level 5
        if isinstance(ctx, P.LetPassThroughContext):
            return ctx.equivExpr()

        # Level 6
        if isinstance(ctx, P.EquivPassThroughContext):
            return ctx.impliesExpr()

        # Level 7
        if isinstance(ctx, P.ImpliesPassThroughContext):
            return ctx.orExpr()

        # Level 8
        if isinstance(ctx, P.OrPassThroughContext):
            return ctx.junctionExpr()

        # Level 9
        if isinstance(ctx, P.AndPassThroughContext):
            return ctx.junctionExpr()

        # Level 10
        if isinstance(ctx, P.JunctionPassThroughContext):
            return ctx.equalityExpr()

        # Levels 11+ — generic try-each chain
        _pass_through_methods = [
            ("equalityExpr", P.EqualityPassThroughContext),
            ("compareExpr", P.ComparePassThroughContext),
            ("setRelExpr", P.SetRelPassThroughContext),
            ("dotsExpr", P.DotsPassThroughContext),
            ("addExpr", P.AddPassThroughContext),
            ("multExpr", P.MultPassThroughContext),
            ("prefixExpr", P.PrefixPassThroughContext),
            ("postfixExpr", P.PostfixPassThroughContext),
            ("applicationExpr", P.ApplicationPassThroughContext),
        ]
        for method_name, pt_cls in _pass_through_methods:
            if isinstance(ctx, pt_cls):
                child = getattr(ctx, method_name, None)
                if callable(child):
                    return child()

        return None

    # ------------------------------------------------------------------
    # Structural construct builders
    # ------------------------------------------------------------------

    def _build_if(self, ctx) -> Block:
        """IF cond THEN a ELSE b → SelectionBlock."""
        P = self._ensure_parser_cls()
        cond_text = _truncate(ctx.ifExpr(0).getText()) if ctx.ifExpr(0) else "?"
        then_block = self._build_expr(ctx.ifExpr(1)) if ctx.ifExpr(1) else EmptyBlock()
        else_block = self._build_expr(ctx.ifExpr(2)) if ctx.ifExpr(2) else EmptyBlock()
        return SelectionBlock(condition=cond_text, then_branch=then_block, else_branch=else_block)

    def _build_case(self, ctx) -> Block:
        """CASE pat -> e [] pat -> e [] OTHER -> e → CaseBlock."""
        arms: list[tuple[str, Block]] = []
        for arm in ctx.caseArm():
            guard = _truncate(arm.expression(0).getText()) if arm.expression(0) else "?"
            body = self._build_expr(arm.expression(1)) if arm.expression(1) else EmptyBlock()
            arms.append((guard, body))
        other = ctx.otherArm()
        if other:
            body = self._build_expr(other.expression()) if other.expression() else EmptyBlock()
            arms.append(("OTHER", body))
        return CaseBlock(arms=arms)

    def _build_let(self, ctx) -> Block:
        """LET def+ IN expr → ScopeBlock."""
        children: list[Block] = []
        for let_def in ctx.letDefinition():
            text = _truncate(let_def.getText())
            children.append(ActionBlock(text=text))
        children.append(self._build_expr(ctx.letExpr()))
        return ScopeBlock(label="LET...IN", children=children)

    def _build_conjunction_list(self, ctx) -> Block:
        r"""`/\` expr `/\` expr ... → SequenceBlock (sequential steps)."""
        children = [self._build_expr(item.expression()) for item in ctx.junctionItem()]
        return SequenceBlock(children=children) if children else EmptyBlock()

    def _build_disjunction_list(self, ctx) -> Block:
        r"""`\/` expr `\/` expr ... → SequenceBlock (alternatives)."""
        children = [self._build_expr(item.expression()) for item in ctx.junctionItem()]
        return SequenceBlock(children=children) if children else EmptyBlock()

    def _build_and_binary(self, ctx) -> Block:
        r"""a `/\` b → SequenceBlock."""
        left = self._build_expr(ctx.andExpr())
        right = self._build_expr(ctx.junctionExpr())
        return SequenceBlock(children=[left, right])

    def _build_or_binary(self, ctx) -> Block:
        r"""a `\/` b → SequenceBlock (alternatives)."""
        left = self._build_expr(ctx.orExpr())
        right = self._build_expr(ctx.andExpr())
        return SequenceBlock(children=[left, right])

    def _build_add_binary(self, ctx) -> Block:
        """Handle inline `/\` (AND/LAND) and `\/` (OR/LOR) at the addExpr level."""
        # LAND/AND → conjunction (sequential steps)
        if ctx.LAND() or ctx.AND():
            left = self._build_expr(ctx.addExpr())
            right = self._build_expr(ctx.multExpr())
            return SequenceBlock(children=[left, right])
        # LOR/OR → disjunction (alternatives)
        if ctx.LOR() or ctx.OR():
            left = self._build_expr(ctx.addExpr())
            right = self._build_expr(ctx.multExpr())
            return SequenceBlock(children=[left, right])
        # Other additive operators → leaf
        return ActionBlock(text=_truncate(ctx.getText()))
