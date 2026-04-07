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
    # Replace multiple whitespaces/newlines with single space
    import re
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


class NassiBuilder:
    """Converts TLA+ expression AST contexts into NSD block trees."""

    # Mapping from pass-through context class names to the getter(s) that retrieve the inner child context.
    # For contexts that have a single child, a single getter name is used.
    # For ExpressionContext, multiple alternatives exist; we try them in order.
    _UNWRAP_MAP: dict[str, list[str]] = {
        "ExpressionContext": [
            "quantifierExpr",
            "lambdaExpression",
            "ifThenElseExpression",
            "caseExpression",
            "letInExpression",
            "equivExpr",
        ],
        "EquivPassThroughContext": ["impliesExpr"],
        "ImpliesPassThroughContext": ["orExpr"],
        "OrPassThroughContext": ["junctionExpr"],
        "AndPassThroughContext": ["junctionExpr"],
        "JunctionPassThroughContext": ["equalityExpr"],
        "EqualityPassThroughContext": ["compareExpr"],
        "ComparePassThroughContext": ["setRelExpr"],
        "SetRelPassThroughContext": ["dotsExpr"],
        "DotsPassThroughContext": ["addExpr"],
        "AddPassThroughContext": ["multExpr"],
        "MultPassThroughContext": ["prefixExpr"],
        "PrefixPassThroughContext": ["postfixExpr"],
        "PostfixPassThroughContext": ["applicationExpr"],
        "ApplicationPassThroughContext": ["primaryExpression"],
        # Quantifier pass-throughs
        "QuantifierPassThroughContext": ["chooseExpr"],
        "ChoosePassThroughContext": ["ifExpr"],
        "IfPassThroughContext": ["caseExpr"],
        "CasePassThroughContext": ["letExpr"],
        "LetPassThroughContext": ["equivExpr"],
    }

    def __init__(self, variables: set[str] | None = None, constants: set[str] | None = None) -> None:
        self._parser_cls: type | None = None
        self.variables = variables or set()
        self.constants = constants or set()

    def _P(self) -> type:
        if self._parser_cls is None:
            from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParser import (
                TLAPLusParser,
            )

            self._parser_cls = TLAPLusParser
        return self._parser_cls

    def _maybe_unwrap(self, ctx) -> object | None:
        """Try to unwrap one pass-through layer using the getter map."""
        tname = type(ctx).__name__
        if tname in self._UNWRAP_MAP:
            getters = self._UNWRAP_MAP[tname]
            for getter_name in getters:
                getter = getattr(ctx, getter_name, None)
                if callable(getter):
                    inner = getter()
                    if inner is not None:
                        return inner
        return None

    def _get_text(self, ctx) -> str:
        if ctx is None:
            return ""
        # Try to get text with original whitespace if possible
        try:
            if hasattr(ctx, "start") and hasattr(ctx, "stop") and ctx.start and ctx.stop:
                stream = ctx.start.getInputStream()
                if stream:
                    return stream.getText(ctx.start.start, ctx.stop.stop)
        except Exception:
            pass
        return ctx.getText()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_all_operators(self, content: str) -> list[tuple[str, Block, int]]:
        """Parse *content* and build an NSD block tree for every operator/theorem/proof.

        Returns a list of ``(name, block_tree, line_number)``.
        """
        from swifta.infrastructure.antlr.parser_adapter import _build_structure_visitor
        from swifta.infrastructure.antlr.runtime import load_generated_types, parse_source_text
        from swifta.domain.model import StructuralElementKind

        generated = load_generated_types()
        result = parse_source_text(content, generated)

        visitor_cls = _build_structure_visitor(generated.visitor_type)
        visitor = visitor_cls()
        visitor.visit(result.tree)

        # Pre-collect symbols for highlight classification
        self.variables = {e.name for e in visitor.elements if e.kind == StructuralElementKind.VARIABLE}
        self.constants = {e.name for e in visitor.elements if e.kind == StructuralElementKind.CONSTANT}

        diagrams: list[tuple[str, Block, int]] = []
        for elem in visitor.elements:
            ctx = visitor.get_context(elem)
            if ctx is None:
                continue

            if elem.kind == StructuralElementKind.OPERATOR_DEFINITION:
                # operator: Op(args) == body
                if hasattr(ctx, "expression"):
                    block = self.build_from_expression(ctx.expression())
                    diagrams.append((elem.name, block, elem.line))

            elif elem.kind == StructuralElementKind.THEOREM:
                # theorem: THEOREM name == statement
                if hasattr(ctx, "expression"):
                    block = self.build_from_expression(ctx.expression())
                    diagrams.append((elem.name, block, elem.line))

            elif elem.kind == StructuralElementKind.PROOF:
                # proof block: could be a full ProofContext or a step (HAVE, ASSERT, QED, etc.)
                ctx_name = type(ctx).__name__
                if ctx_name == "ProofContext":
                    block = self._build_proof(ctx)
                else:
                    # It's a proof step or QED
                    block = self._build_step(ctx)
                if block:
                    diagrams.append((elem.name, block, elem.line))

        return diagrams

    def build_from_expression(self, expr_ctx) -> Block:
        """Build NSD block from an ANTLR *expression* context."""
        return self._build(expr_ctx)

    # ------------------------------------------------------------------
    # Core recursive builder
    # ------------------------------------------------------------------

    def _build(self, ctx) -> Block:  # noqa: C901
        """Recursively build NSD block from ANTLR context."""
        if ctx is None:
            return EmptyBlock()

        tname = type(ctx).__name__

        # --- Direct structural constructs ---
        if tname == "IfThenElseExpressionContext":
            return self._build_if(ctx)
        if tname == "CaseExpressionContext":
            return self._build_case(ctx)
        if tname == "LetInExpressionContext":
            return self._build_let(ctx)
        if tname == "ExceptExpressionContext":
            return self._build_except(ctx)
        if tname == "ConjunctionListContext":
            return self._build_conjunction_list(ctx)
        if tname == "DisjunctionListContext":
            return self._build_disjunction_list(ctx)
        if tname == "AndBinaryExprContext":
            return self._build_and_binary(ctx)
        if tname == "OrBinaryExprContext":
            return self._build_or_binary(ctx)

        # --- Leaf quantifiers / CHOOSE ---
        if tname == "QuantifierExpressionContext":
            return self._build_quantifier(ctx)
        if tname == "TemporalQuantifierExpressionContext":
            return self._build_quantifier(ctx)
        if tname == "ChooseExpressionContext":
            return self._build_choose(ctx)
        if tname == "SetConstructorContext":
            return self._build_set_constructor(ctx)
        if tname == "FunctionConstructorContext":
            return self._build_function_constructor(ctx)
        if tname == "LambdaExpressionContext":
            return self._build_lambda(ctx)

        # --- Unwrap pass-through layers (ExpressionContext, EquivPassThrough, etc.) ---
        inner = self._maybe_unwrap(ctx)
        if inner is not None:
            return self._build(inner)

        # --- Binary expression nodes: scan for hidden structural children ---
        if "BinaryExprContext" in tname or "BinaryExpressionContext" in tname:
            structural = self._scan_children(ctx)
            if structural is not None:
                return structural
            return ActionBlock(text=self._highlight_identifiers(_truncate(self._get_text(ctx))))

        # --- Generic child scan for any other wrapper ---
        structural = self._scan_children(ctx)
        if structural is not None:
            return structural

        # --- Fallback leaf ---
        return ActionBlock(text=self._highlight_identifiers(_truncate(self._get_text(ctx))))

    # ------------------------------------------------------------------
    # Structural construct builders
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
            if tname == "ExceptExpressionContext":
                return self._build_except(child)
            if tname == "ConjunctionListContext":
                return self._build_conjunction_list(child)
            if tname == "DisjunctionListContext":
                return self._build_disjunction_list(child)
            if tname == "AndBinaryExprContext":
                return self._build_and_binary(child)
            if tname == "OrBinaryExprContext":
                return self._build_or_binary(child)

            # Recurse into non-structural children
            result = self._scan_children(child)
            if result is not None:
                return result

        return None

    # ------------------------------------------------------------------
    # Structural construct builders
    # ------------------------------------------------------------------

    def _build_if(self, ctx) -> Block:
        cond_text = _truncate(self._get_text(ctx.ifExpr(0))) if ctx.ifExpr(0) else "?"
        then_block = self._build(ctx.ifExpr(1)) if ctx.ifExpr(1) else EmptyBlock()
        else_block = self._build(ctx.ifExpr(2)) if ctx.ifExpr(2) else EmptyBlock()
        return SelectionBlock(condition=cond_text, then_branch=then_block, else_branch=else_block)

    def _build_case(self, ctx) -> Block:
        arms: list[tuple[str, Block]] = []
        for arm in ctx.caseArm():
            guard = _truncate(self._get_text(arm.expression(0))) if arm.expression(0) else "?"
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
            text = _truncate(self._get_text(let_def))
            children.append(ActionBlock(text=text))
        children.append(self._build(ctx.letExpr()))
        return ScopeBlock(label="LET...IN", children=children)

    def _build_quantifier(self, ctx) -> Block:
        # Extract the quantifier part: \A x \in S :
        full_text = self._get_text(ctx)
        # Try to split at COLON to separate head and body
        if ":" in full_text:
            head, body_text = full_text.split(":", 1)
            return ScopeBlock(label=f"{_truncate(head)} :", children=[self._build(ctx.quantifierExpr())])
        return ActionBlock(text=_truncate(full_text))

    def _build_choose(self, ctx) -> Block:
        full_text = self._get_text(ctx)
        if ":" in full_text:
            head, body_text = full_text.split(":", 1)
            return ScopeBlock(label=f"{_truncate(head)} :", children=[self._build(ctx.chooseExpr())])
        return ActionBlock(text=_truncate(full_text))

    def _build_set_constructor(self, ctx) -> Block:
        # { x \in S : expression }
        full_text = self._get_text(ctx)
        if ":" in full_text:
            head, body_text = full_text.split(":", 1)
            # Remove closing RCURLY from body if it's there? No, the rule handles inner too.
            return ScopeBlock(label=f"{_truncate(head)} :", children=[self._build(ctx.expression())])
        return ActionBlock(text=_truncate(full_text))

    def _build_function_constructor(self, ctx) -> Block:
        # [ x \in S |-> expression ]
        full_text = self._get_text(ctx)
        # ARROW is |->
        if "|->" in full_text:
            head, body_text = full_text.split("|->", 1)
            return ScopeBlock(label=f"{_truncate(head)} |->", children=[self._build(ctx.expression())])
        return ActionBlock(text=_truncate(full_text))

    def _build_lambda(self, ctx) -> Block:
        full_text = self._get_text(ctx)
        if ":" in full_text:
            head, body_text = full_text.split(":", 1)
            return ScopeBlock(label=f"{_truncate(head)} :", children=[self._build(ctx.expression())])
        return ActionBlock(text=_truncate(full_text))

    def _build_conjunction_list(self, ctx) -> Block:
        # In the TLA+ grammar, ConjunctionListContext has multiple expression() children (ignoring AND tokens)
        exprs = ctx.expression()
        children = [self._build(e) for e in exprs]
        return SequenceBlock(children=children) if children else EmptyBlock()

    def _build_disjunction_list(self, ctx) -> Block:
        exprs = ctx.expression()
        children = [self._build(e) for e in exprs]
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

        # Not a logical operator → treat as leaf action
        return ActionBlock(text=_truncate(self._get_text(ctx)))

    # ------------------------------------------------------------------
    # Proof and theorem step builders
    # ------------------------------------------------------------------

    def _build_proof(self, ctx) -> Block:
        """Build a NSD block for a PROOF construct."""
        # Check for OBVIOUS or OMITTED
        if ctx.OBVIOUS_KW():
            return ActionBlock(text="OBVIOUS")
        if ctx.OMITTED_KW():
            return ActionBlock(text="OMITTED")

        # Check for terminalProof: BY ...
        if ctx.terminalProof():
            tproof = ctx.terminalProof()
            text = "BY ..." if tproof.BY_KW() else "PROOF"
            return ActionBlock(text=text)

        # Build from step* qedStep
        steps = list(ctx.step()) if hasattr(ctx, "step") and ctx.step() else []
        qed = ctx.qedStep() if hasattr(ctx, "qedStep") and ctx.qedStep() else None

        blocks: list[Block] = []
        for step_ctx in steps:
            step_block = self._build_step(step_ctx)
            if step_block:
                blocks.append(step_block)

        if qed:
            blocks.append(ActionBlock(text="QED"))

        return SequenceBlock(children=blocks) if blocks else ActionBlock(text="PROOF")

    def _get_step_number(self, ctx) -> str | None:
        """Extract step number from proof step context (e.g., '<1>', '<2>1.')."""
        # Check current context
        if hasattr(ctx, "stepStartToken"):
            token = ctx.stepStartToken()
            if token:
                return token.getText()
        # Walk up parents to find a StepContext (or QedStepContext) with stepStartToken
        # ANTLR4 Python uses parentCtx
        parent = getattr(ctx, "parentCtx", getattr(ctx, "parent", None))
        while parent:
            if hasattr(parent, "stepStartToken"):
                token = parent.stepStartToken()
                if token:
                    return token.getText()
            parent = getattr(parent, "parentCtx", getattr(parent, "parent", None))
        return None

    def _build_step(self, ctx) -> Block | None:
        """Build a block for a proof step."""
        prefix = self._get_step_number(ctx)

        # QED step
        if type(ctx).__name__ == "QedStepContext":
            block = ActionBlock(text="QED")
        elif hasattr(ctx, "useOrHide") and ctx.useOrHide():
            block = self._build_use_or_hide(ctx.useOrHide())
        elif hasattr(ctx, "instantiation") and ctx.instantiation():
            block = self._build_instantiation_step(ctx.instantiation())
        elif hasattr(ctx, "defStep") and ctx.defStep():
            block = self._build_def_step(ctx.defStep())
        elif hasattr(ctx, "haveStep") and ctx.haveStep():
            block = self._build_have_step(ctx.haveStep())
        elif hasattr(ctx, "takeStep") and ctx.takeStep():
            block = self._build_take_step(ctx.takeStep())
        elif hasattr(ctx, "witnessStep") and ctx.witnessStep():
            block = self._build_witness_step(ctx.witnessStep())
        elif hasattr(ctx, "pickStep") and ctx.pickStep():
            block = self._build_pick_step(ctx.pickStep())
        elif hasattr(ctx, "caseStep") and ctx.caseStep():
            block = self._build_case_step(ctx.caseStep())
        elif hasattr(ctx, "assertStep") and ctx.assertStep():
            block = self._build_assert_step(ctx.assertStep())
        else:
            block = None

        if block and prefix:
            block = ActionBlock(text=f"{prefix} {block.text}")
        return block

    def _build_use_or_hide(self, ctx) -> Block:
        text = _truncate(self._get_text(ctx), 60)
        return ActionBlock(text=text)

    def _build_def_step(self, ctx) -> Block:
        parts = []
        for defn in ctx.operatorOrFunctionDefinition():
            parts.append(_truncate(self._get_text(defn), 40))
        text = "DEFINE " + ", ".join(parts) if parts else "DEFINE"
        return ActionBlock(text=text)

    def _build_have_step(self, ctx) -> Block:
        text = _truncate(self._get_text(ctx), 60)
        return ActionBlock(text=text)

    def _build_take_step(self, ctx) -> Block:
        text = _truncate(self._get_text(ctx), 60)
        return ActionBlock(text=text)

    def _build_witness_step(self, ctx) -> Block:
        text = _truncate(self._get_text(ctx), 60)
        return ActionBlock(text=text)

    def _build_pick_step(self, ctx) -> Block:
        text = _truncate(self._get_text(ctx), 60)
        return ActionBlock(text=text)

    def _build_case_step(self, ctx) -> Block:
        text = _truncate(self._get_text(ctx), 60)
        return ActionBlock(text=text)

    def _build_assert_step(self, ctx) -> Block:
        text = _truncate(self._get_text(ctx), 60)
        # Prepend ASSERT if the code doesn't have a specific keyword
        if not text.startswith(("ASSERT", "SUFFICES", "THEOREM", "PROPOSITION", "LEMMA", "COROLLARY")):
             text = f"ASSERT {text}"
        return ActionBlock(text=text)

    def _build_instantiation_step(self, ctx) -> Block:
        module_ref = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else "?"
        return ActionBlock(text=f"INSTANCE {module_ref}")

    def _build_except(self, ctx) -> Block:
        # ctx is ExceptExpressionContext
        # rule: expression EXCEPT_KW exceptSpec (COMMA exceptSpec)*
        base_expr = ctx.expression()
        base_text = self._highlight_identifiers(_truncate(self._get_text(base_expr))) if base_expr else "?"
        
        specs = ctx.exceptSpec()
        update_blocks: list[Block] = []
        for spec in specs:
             # spec: BANG exceptComponent+ EQUALS expression
             components = spec.exceptComponent()
             comp_parts = []
             for comp in components:
                 comp_parts.append(self._get_text(comp))
             
             path = "".join(comp_parts)
             val_expr = spec.expression()
             val_text = self._highlight_identifiers(_truncate(self._get_text(val_expr))) if val_expr else "?"
             
             update_blocks.append(ActionBlock(text=f"!{path} = {val_text}"))
        
        content = SequenceBlock(children=update_blocks) if len(update_blocks) > 1 else update_blocks[0]
        return ScopeBlock(label=f"Update {base_text}:", children=[content])

    def _highlight_identifiers(self, text: str) -> str:
        """Apply KaTeX color markers to known variables and constants."""
        if not self.variables and not self.constants:
            return text
        
        import re
        # We only want to highlight standalone identifiers that aren't keywords
        # TLA+ identifiers: [a-zA-Z_][a-zA-Z0-9_]*
        def repl(match):
            name = match.group(0)
            if name in self.variables:
                # Teal-ish color for variables
                return f"\\color{{#1abc9c}}{{{name}}}"
            if name in self.constants:
                # Amber/Orange color for constants
                return f"\\color{{#f39c12}}{{{name}}}"
            return name

        # Simple regex for identifiers
        return re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", repl, text)
