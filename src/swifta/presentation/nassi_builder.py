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
    """Converts TLA+ expression AST contexts into NSD block trees.

    Strategy: recursively scan the ANTLR parse tree depth-first, looking
    for "structural" constructs (IF, CASE, LET, conjunction, disjunction)
    at any precedence level.  Pass-through layers are unwrapped transparently.
    Binary expression nodes (comparisons, arithmetic) that don't carry NSD
    semantics are treated as leaves.
    """

    def __init__(self) -> None:
        self._parser_cls: type | None = None

    def _P(self) -> type:
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
        return self._build(expr_ctx)

    # ------------------------------------------------------------------
    # Core recursive builder
    # ------------------------------------------------------------------

    def _build(self, ctx) -> Block:  # noqa: C901
        P = self._P()

        if ctx is None:
            return EmptyBlock()

        tname = type(ctx).__name__

        # ---- Structural constructs ----

        if tname == "IfThenElseExpressionContext":
            return self._build_if(ctx)

        if tname == "CaseExpressionContext":
            return self._build_case(ctx)

        if tname == "LetInExpressionContext":
            return self._build_let(ctx)

        if tname == "ConjunctionListContext":
            return self._build_conjunction_list(ctx)

        if tname == "DisjunctionListContext":
            return self._build_disjunction_list(ctx)

        if tname == "AndBinaryExprContext":
            return self._build_and_binary(ctx)

        if tname == "OrBinaryExprContext":
            return self._build_or_binary(ctx)

        # Inline /\ and \/ at the addExpr level
        if tname == "AddBinaryExprContext":
            return self._build_add_binary(ctx)

        # ---- Quantifier / CHOOSE → leaf ----
        if tname in ("QuantifierExpressionContext", "TemporalQuantifierExpressionContext",
                      "ChooseExpressionContext"):
            return ActionBlock(text=_truncate(ctx.getText()))

        # ---- Binary expression nodes that may hide structural children ----
        # If a binary context (comparison, equality, equiv, implies) contains
        # an AddBinary with AND/LAND/OR/LOR deep inside, we must find it.
        if "BinaryExprContext" in tname or "BinaryExpressionContext" in tname:
            structural = self._find_structural_in_binary(ctx)
            if structural is not None:
                return structural
            # No structural child → whole thing is a leaf
            return ActionBlock(text=_truncate(ctx.getText()))

        # ---- Pass-through unwrapping ----
        unwrapped = self._unwrap(ctx)
        if unwrapped is not None:
            return self._build(unwrapped)

        # ---- Leaf ----
        return ActionBlock(text=_truncate(ctx.getText()))

    # ------------------------------------------------------------------
    # Deep-scan binary expressions for hidden structural constructs
    # ------------------------------------------------------------------

    def _find_structural_in_binary(self, ctx) -> Block | None:
        """Check if a binary expression node contains a structural construct
        (like AddBinary with AND/LAND) hidden inside its children.

        This handles cases like ``x >= 0 /\\ y >= 0`` where the ``/\\`` is
        at the addExpr level but wrapped inside a CompareBinary node.
        """
        # Get the "left" child via the standard method pattern.
        # Binary expr contexts have a method named after their rule (e.g. compareExpr)
        # that returns the left operand, and another method for the right operand.
        # We recursively scan ALL children looking for structural constructs.
        structural = self._scan_children(ctx)
        if structural is not None:
            return structural
        return None

    def _scan_children(self, ctx) -> Block | None:
        """Recursively scan all children of *ctx* for structural constructs."""
        P = self._P()
        if not hasattr(ctx, "children") or ctx.children is None:
            return None

        for child in ctx.children:
            # Only interested in rule contexts (not tokens)
            if not hasattr(child, "getText"):
                continue

            tname = type(child).__name__

            # Direct structural matches
            if tname == "IfThenElseExpressionContext":
                return self._build_if(child)
            if tname == "CaseExpressionContext":
                return self._build_case(child)
            if tname == "LetInExpressionContext":
                return self._build_let(child)
            if tname == "ConjunctionListContext":
                return self._build_conjunction_list(child)
            if tname == "DisjunctionListContext":
                return self._build_disjunction_list(child)
            if tname == "AndBinaryExprContext":
                return self._build_and_binary(child)
            if tname == "OrBinaryExprContext":
                return self._build_or_binary(child)
            if tname == "AddBinaryExprContext":
                result = self._build_add_binary(child)
                if not isinstance(result, ActionBlock):
                    return result

            # Recurse into non-structural children
            result = self._scan_children(child)
            if result is not None:
                return result

        return None

    # ------------------------------------------------------------------
    # Pass-through unwrapping
    # ------------------------------------------------------------------

    # Chain: (context_class_suffix, method_to_call)
    _UNWRAP_CHAIN: list[tuple[str, str]] = [
        ("ExpressionContext", "quantifierExpr"),
        ("QuantifierPassThroughContext", "chooseExpr"),
        ("ChoosePassThroughContext", "ifExpr"),
        ("IfPassThroughContext", "caseExpr"),
        ("CasePassThroughContext", "letExpr"),
        ("LetPassThroughContext", "equivExpr"),
        ("EquivPassThroughContext", "impliesExpr"),
        ("ImpliesPassThroughContext", "orExpr"),
        ("OrPassThroughContext", "andExpr"),
        ("AndPassThroughContext", "junctionExpr"),
        ("JunctionPassThroughContext", "equalityExpr"),
        ("EqualityPassThroughContext", "compareExpr"),
        ("ComparePassThroughContext", "setRelExpr"),
        ("SetRelPassThroughContext", "dotsExpr"),
        ("DotsPassThroughContext", "addExpr"),
        ("AddPassThroughContext", "multExpr"),
        ("MultPassThroughContext", "prefixExpr"),
        ("PrefixPassThroughContext", "postfixExpr"),
        ("PostfixPassThroughContext", "applicationExpr"),
        ("ApplicationPassThroughContext", "primaryExpression"),
    ]

    def _unwrap(self, ctx):
        """Unwrap one pass-through layer.  Returns inner context or ``None``."""
        tname = type(ctx).__name__
        for suffix, method in self._UNWRAP_CHAIN:
            if tname == suffix:
                getter = getattr(ctx, method, None)
                if callable(getter):
                    return getter()
        return None

    # ------------------------------------------------------------------
    # Structural construct builders
    # ------------------------------------------------------------------

    def _build_if(self, ctx) -> Block:
        cond_text = _truncate(ctx.ifExpr(0).getText()) if ctx.ifExpr(0) else "?"
        then_block = self._build(ctx.ifExpr(1)) if ctx.ifExpr(1) else EmptyBlock()
        else_block = self._build(ctx.ifExpr(2)) if ctx.ifExpr(2) else EmptyBlock()
        return SelectionBlock(condition=cond_text, then_branch=then_block, else_branch=else_block)

    def _build_case(self, ctx) -> Block:
        arms: list[tuple[str, Block]] = []
        for arm in ctx.caseArm():
            guard = _truncate(arm.expression(0).getText()) if arm.expression(0) else "?"
            body = self._build(arm.expression(1)) if arm.expression(1) else EmptyBlock()
            arms.append((guard, body))
        other = ctx.otherArm()
        if other:
            body = self._build(other.expression()) if other.expression() else EmptyBlock()
            arms.append(("OTHER", body))
        return CaseBlock(arms=arms)

    def _build_let(self, ctx) -> Block:
        children: list[Block] = []
        for let_def in ctx.letDefinition():
            text = _truncate(let_def.getText())
            children.append(ActionBlock(text=text))
        children.append(self._build(ctx.letExpr()))
        return ScopeBlock(label="LET...IN", children=children)

    def _build_conjunction_list(self, ctx) -> Block:
        children = [self._build(item.expression()) for item in ctx.junctionItem()]
        return SequenceBlock(children=children) if children else EmptyBlock()

    def _build_disjunction_list(self, ctx) -> Block:
        children = [self._build(item.expression()) for item in ctx.junctionItem()]
        return SequenceBlock(children=children) if children else EmptyBlock()

    def _build_and_binary(self, ctx) -> Block:
        left = self._build(ctx.andExpr())
        right = self._build(ctx.junctionExpr())
        return SequenceBlock(children=[left, right])

    def _build_or_binary(self, ctx) -> Block:
        left = self._build(ctx.orExpr())
        right = self._build(ctx.andExpr())
        return SequenceBlock(children=[left, right])

    def _build_add_binary(self, ctx) -> Block:
        r"""Inline ``/\`` and ``\/`` at the addExpr level.

        The grammar now correctly routes inline operators through AndBinaryExpr
        and OrBinaryExpr (after grammar fix: OrPassThrough uses andExpr).
        Decompose conjunction/disjunction into SequenceBlock; other additive
        operators (arithmetic, set ops) remain flat.
        """
        is_conj = ctx.AND() is not None or ctx.LAND() is not None
        is_disj = ctx.OR() is not None or ctx.LOR() is not None

        if is_conj or is_disj:
            left = self._build(ctx.addExpr())
            right = self._build(ctx.multExpr())
            return SequenceBlock(children=[left, right])

        return ActionBlock(text=_truncate(ctx.getText()))
