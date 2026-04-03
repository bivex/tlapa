"""ANTLR-backed TLA+ parser adapter."""

from __future__ import annotations

from time import perf_counter

from swifta.domain.model import (
    GrammarVersion,
    ParseOutcome,
    ParseStatistics,
    SourceUnit,
    StructuralElement,
    StructuralElementKind,
    SyntaxDiagnostic,
)
from swifta.domain.ports import TlaplusSyntaxParser
from swifta.infrastructure.antlr.error_listener import format_diagnostic
from swifta.infrastructure.antlr.runtime import (
    ANTLR_GRAMMAR_VERSION,
    get_global_cache,
    load_generated_types,
    parse_source_text,
)


_NOT_IDENTIFIER_RE = frozenset(
    {
        "ASSUME",
        "ASSUMPTION",
        "AXIOM",
        "PROOF",
        "PROVE",
        "QED",
        "OBVIOUS",
        "OMITTED",
        "DEFINE",
        "BY",
        "HAVE",
        "TAKE",
        "WITNESS",
        "PICK",
        "CASE",
        "SUFFICES",
        "USE",
        "HIDE",
        "INSTANCE",
        "WITH",
        "IF",
        "THEN",
        "ELSE",
        "LET",
        "IN",
        "LOCAL",
        "EXTENDS",
        "CHOOSE",
        "NEW",
        "RECURSIVE",
        "CONSTANT",
        "CONSTANTS",
        "VARIABLE",
        "VARIABLES",
        "WF_",
        "SF_",
        "LAMBDA",
        "ENABLED",
        "UNCHANGED",
        "DOMAIN",
        "SUBSET",
        "UNION",
        "OTHER",
    }
)


_FALSE_POSITIVE_PATTERNS = (
    "no viable alternative",
    "mismatched input",
    "extraneous input",
    "missing def",
    "expecting {and, or}",
)


_TRUE_PATTERNS = (
    "missing '====' to close the module",
    "add '====' to close the module",
    "module end marker",
    "start the module with '---- MODULE",
    "unclosed set expression, add '}' to close",
    "unclosed bracket expression, add ']' to close",
    "unclosed parenthesized expression, add ')' to close",
    "backslash operators must be followed by a keyword (e.g., \\in, \\E, \\A)",
    "unexpected token; check operator spelling and TLA+ syntax",
    "use '<<' for tuple start, not '<'",
    "use '>>' for tuple end, not '>'",
)


_TLA_FIX_TABLE = tuple(
    (pattern, suggestion, category)
    for pattern, suggestion, category in [
        (
            r"mismatched input '(\w+)' expecting",
            r"did you mean to use '\\%s' as an operator?",
            "operator",
        ),
        (
            r"extraneous input '===='",
            "remove extra '=' characters after the module end marker",
            "end_module",
        ),
        (
            r"no viable alternative at input",
            "check for missing operators, unmatched parentheses, or invalid syntax",
            "syntax",
        ),
        (r"missing '===='", "add '====' to close the module", "end_module"),
        (r"missing '----'", "start the module with '---- MODULE <name> ----'", "begin_module"),
        (r"mismatched input '<'", "use '<<' for tuple start, not '<'", "tuple"),
        (r"mismatched input '>'", "use '>>' for tuple end, not '>'", "tuple"),
        (r"missing '}'", "unclosed set expression, add '}' to close", "set"),
        (r"missing ']'", "unclosed bracket expression, add ']' to close", "bracket"),
        (r"missing '\)'", "unclosed parenthesized expression, add ')' to close", "paren"),
        (
            r"mismatched input '\\\\'",
            r"backslash operators must be followed by a keyword (e.g., \\in, \E, \A)",
            "backslash",
        ),
        (r"expecting", "unexpected token; check operator spelling and TLA+ syntax", "syntax"),
    ]
)


_MAX_TEXT_LEN = 120
_MAX_SIG_LEN = 80


def _truncate(text: str, limit: int = _MAX_TEXT_LEN) -> str:
    return text[: limit - 3] + "..." if len(text) > limit else text


class AntlrTlaplusSyntaxParser(TlaplusSyntaxParser):
    def __init__(self, *, diags_enabled: bool = True, cache_enabled: bool = True) -> None:
        self._generated = load_generated_types()
        self._cache = get_global_cache() if cache_enabled else None
        self._diags_enabled = diags_enabled
        self._source_lines: list[str] | None = None
        self._source: str = ""

    @property
    def grammar_version(self) -> GrammarVersion:
        return ANTLR_GRAMMAR_VERSION

    @grammar_version.setter
    def grammar_version(self, value: str | None) -> None:
        self._source = value or ""
        if value:
            self._line_map = {i: i + 1 for i, line in enumerate(value.splitlines())}

    def parse(self, source_unit: SourceUnit) -> ParseOutcome:
        started_at = perf_counter()
        try:
            parse_result = parse_source_text(
                source_unit.content,
                self._generated,
                use_cache=self._cache is not None,
            )
            visitor = _build_structure_visitor(self._generated.visitor_type)()
            visitor.visit(parse_result.tree)
            self._source_lines = source_unit.content.splitlines()

            elements = tuple(visitor.elements)
            elapsed_ms = round((perf_counter() - started_at) * 1000, 3)

            diagnostics = (
                _classify_diagnostics(parse_result.diagnostics, source_unit.content)
                if self._diags_enabled
                else ()
            )

            return ParseOutcome.success(
                source_unit=source_unit,
                grammar_version=self.grammar_version,
                diagnostics=diagnostics,
                structural_elements=elements,
                statistics=ParseStatistics(
                    token_count=len(parse_result.token_stream.tokens),
                    structural_element_count=len(elements),
                    diagnostic_count=len(diagnostics),
                    elapsed_ms=elapsed_ms,
                ),
            )
        except Exception as error:
            elapsed_ms = round((perf_counter() - started_at) * 1000, 3)
            return ParseOutcome.technical_failure(
                source_unit=source_unit,
                grammar_version=self.grammar_version,
                message=str(error),
                elapsed_ms=elapsed_ms,
            )

    def clear_cache(self) -> None:
        if self._cache:
            self._cache.clear()

    def format_diagnostics_report(self, diagnostics: tuple[SyntaxDiagnostic, ...]) -> str:
        if not self._source_lines:
            return ""
        lines = self._source_lines
        parts = []
        for diag in diagnostics:
            parts.append(format_diagnostic(diag, lines))
        return "\n".join(parts)


def _classify_diagnostics(
    diagnostics: tuple[SyntaxDiagnostic, ...], source_content: str | None
) -> tuple[SyntaxDiagnostic, ...]:
    if not source_content:
        return diagnostics

    warnings: list[SyntaxDiagnostic] = []
    errors: list[SyntaxDiagnostic] = []

    for diag in diagnostics:
        msg = diag.message.lower()
        is_false_positive = any(p in msg for p in _FALSE_POSITIVE_PATTERNS)
        is_true_error = any(p in msg for p in _TRUE_PATTERNS)

        if is_false_positive:
            warnings.append(_downgrade_diagnostic(diag))
        elif is_true_error:
            errors.append(diag)
        else:
            warnings.append(_downgrade_diagnostic(diag))

    return tuple(errors + warnings)


def _downgrade_diagnostic(diag: SyntaxDiagnostic) -> SyntaxDiagnostic:
    from swifta.domain.model import DiagnosticSeverity

    return SyntaxDiagnostic(
        severity=DiagnosticSeverity.WARNING,
        message=diag.message,
        line=diag.line,
        column=diag.column,
    )


def _format_warning_msg(
    diagnostics: tuple[SyntaxDiagnostic, ...], warnings: list[SyntaxDiagnostic]
) -> str:
    parts = []
    parts.append(f"{len(warnings)} expression-level diagnostic(s) filtered as warnings")
    for w in warnings:
        parts.append(f"  L{w.line}:{w.column} {w.message}")
    if len(parts) > 7:
        parts.append(f"  ... and {len(parts) - 6} more")
    return "\n".join(parts)


def _build_structure_visitor(visitor_base: type) -> type:
    """Build a visitor that walks the TLA+ parse tree and extracts structural elements."""

    class TlaplusStructureVisitor(visitor_base):
        def __init__(self) -> None:
            super().__init__()
            self.elements: list[StructuralElement] = []
            self._contexts: list[tuple[StructuralElement, object]] = []
            self._module_name: str | None = None
            self._in_proof: bool = False
            self._proof_step_counter: int = 0

        def get_context(self, element: StructuralElement) -> object | None:
            for e, ctx in self._contexts:
                if e is element:
                    return ctx
            return None

        def _append(self, kind, name: str, ctx, signature: str | None = None) -> StructuralElement:
            container = self._module_name
            line = ctx.start.line if hasattr(ctx, "start") and ctx.start else 0
            column = ctx.start.column if hasattr(ctx, "start") and ctx.start else 0
            element = StructuralElement(
                kind=kind,
                name=name,
                line=line,
                column=column,
                container=container,
                signature=signature,
            )
            self.elements.append(element)
            self._contexts.append((element, ctx))
            return element

        # -- Module-level constructs --

        def visitFirstModule(self, ctx):
            sep_tok = ctx.SEPARATOR()
            if not sep_tok:
                return None
            if not sep_tok.getText().startswith("----"):
                return None
            ident = ctx.IDENTIFIER()
            if ident:
                name = ident.getText()
                self._module_name = name
                self._append(StructuralElementKind.MODULE, name, ctx)
            body = ctx.moduleBody()
            if body:
                for child in body.getChildren():
                    self.visit(child)
            return None

        def visitModule(self, ctx):
            sep_tok = ctx.SEPARATOR()
            if not sep_tok:
                return None
            if not sep_tok.getText().startswith("----"):
                return None
            ident = ctx.IDENTIFIER()
            if ident:
                name = ident.getText()
                self._module_name = name
                self._append(StructuralElementKind.MODULE, name, ctx)
            body = ctx.moduleBody()
            if body:
                for child in body.getChildren():
                    self.visit(child)
            return None

        def visitExtends(self, ctx):
            for ident in ctx.IDENTIFIER():
                self._append(StructuralElementKind.EXTENDS, ident.getText(), ctx)
            return None

        # -- Declarations --

        def visitVariableDeclaration(self, ctx):
            for ident in ctx.IDENTIFIER():
                self._append(
                    StructuralElementKind.VARIABLE,
                    ident.getText(),
                    ctx,
                    signature=f"VARIABLE {ident.getText()}",
                )
            return None

        def visitParameterDeclaration(self, ctx):
            for item in ctx.constantDeclItem():
                name = self._extract_decl_name(item)
                self._append(
                    StructuralElementKind.CONSTANT,
                    name,
                    ctx,
                    signature=f"CONSTANT {name}",
                )
            return None

        def visitRecursiveDeclaration(self, ctx):
            for item in ctx.constantDeclItem():
                name = self._extract_decl_name(item)
                self._append(
                    StructuralElementKind.RECURSIVE,
                    name,
                    ctx,
                    signature=f"RECURSIVE {name}",
                )
            return None

        # -- Definitions --

        def visitOperatorDefinition(self, ctx):
            name = self._extract_def_name(ctx)
            if name is None or not self._is_definition_name_valid(name):
                return None
            raw_lhs = self._raw_def_lhs(ctx)
            signature = self._build_signature(raw_lhs, name)
            self._append(
                StructuralElementKind.OPERATOR_DEFINITION,
                name,
                ctx,
                signature=signature,
            )
            return None

        def visitFunctionDefinition(self, ctx):
            name = self._extract_func_def_name(ctx)
            if name is None or not self._is_definition_name_valid(name):
                return None
            self._append(
                StructuralElementKind.FUNCTION_DEFINITION,
                name,
                ctx,
                signature=f"{name}[...] == ...",
            )
            return None

        def visitModuleDefinition(self, ctx):
            return None

        def _is_definition_name_valid(self, name: str) -> bool:
            if not name or " " in name:
                return False
            if name.startswith("\\"):
                after = name[1:]
                return after.isalpha() and len(name) <= 12
            return all(c.isalnum() or c in "_." for c in name)

        # -- Instance --

        def visitInstance(self, ctx):
            inst = ctx.instantiation()
            if inst:
                module_ref = inst.IDENTIFIER().getText() if inst.IDENTIFIER() else "?"
                self._append(
                    StructuralElementKind.INSTANCE,
                    module_ref,
                    ctx,
                    signature=f"INSTANCE {module_ref}",
                )
            return None

        # -- Assumptions and Theorems --

        def visitAssumption(self, ctx):
            name = None
            if ctx.IDENTIFIER():
                name = ctx.IDENTIFIER().getText()
            self._append(
                StructuralElementKind.ASSUMPTION,
                name or "ASSUME",
                ctx,
            )
            return None

        def visitTheorem(self, ctx):
            name = None
            if ctx.IDENTIFIER():
                name = ctx.IDENTIFIER().getText()
            self._append(
                StructuralElementKind.THEOREM,
                name or "THEOREM",
                ctx,
                signature=f"THEOREM {name}" if name else "THEOREM",
            )
            return self.visitChildren(ctx)

        # -- Proof construct visitors --

        def visitProof(self, ctx):
            self._in_proof = True
            self._proof_step_counter = 0
            self._append(StructuralElementKind.PROOF, "PROOF", ctx)
            result = self.visitChildren(ctx)
            self._in_proof = False
            return result

        def visitUseOrHide(self, ctx):
            is_use = ctx.USE_KW() is not None
            is_hide = ctx.HIDE_KW() is not None
            if is_use:
                kind = StructuralElementKind.USE
            elif is_hide:
                kind = StructuralElementKind.HIDE
            else:
                kind = StructuralElementKind.USE
            text = _truncate(ctx.getText(), 60)
            self._append(kind, text, ctx)
            return None

        def visitStep(self, ctx):
            self._proof_step_counter += 1
            children = list(ctx.getChildren()) if hasattr(ctx, "children") and ctx.children else []
            for child in children:
                child_name = type(child).__name__
                if child_name == "DefStepContext":
                    self._visit_def_step(child)
                elif child_name == "HaveStepContext":
                    self._visit_have_step(child)
                elif child_name == "TakeStepContext":
                    self._visit_take_step(child)
                elif child_name == "WitnessStepContext":
                    self._visit_witness_step(child)
                elif child_name == "PickStepContext":
                    self._visit_pick_step(child)
                elif child_name == "CaseStepContext":
                    self._visit_case_step(child)
                elif child_name == "AssertStepContext":
                    self._visit_assert_step(child)
                else:
                    self.visit(child)
            return None

        def visitQedStep(self, ctx):
            self._append(
                StructuralElementKind.PROOF,
                "QED",
                ctx,
                signature="QED",
            )
            return self.visitChildren(ctx)

        def _visit_def_step(self, ctx):
            for defn in ctx.operatorOrFunctionDefinition():
                self.visit(defn)
            return None

        def _visit_have_step(self, ctx):
            expr_ctx = ctx.expression()
            if expr_ctx:
                self._append(
                    StructuralElementKind.PROOF,
                    "HAVE",
                    expr_ctx,
                    signature=f"HAVE {expr_ctx.getText()[:60]}",
                )
            return None

        def _visit_take_step(self, ctx):
            text = _truncate(ctx.getText(), 80) if ctx.getText() else "TAKE"
            self._append(StructuralElementKind.PROOF, "TAKE", ctx, signature=text)
            return None

        def _visit_witness_step(self, ctx):
            exprs = ctx.expression()
            witness_text = ", ".join(e.getText() for e in exprs) if exprs else ""
            self._append(
                StructuralElementKind.PROOF,
                "WITNESS",
                ctx,
                signature=f"WITNESS {witness_text}",
            )
            return None

        def _visit_pick_step(self, ctx):
            text = _truncate(ctx.getText(), 80) if ctx.getText() else "PICK"
            self._append(StructuralElementKind.PROOF, "PICK", ctx, signature=text)
            return None

        def _visit_case_step(self, ctx):
            expr_ctx = ctx.expression()
            if expr_ctx:
                self._append(
                    StructuralElementKind.PROOF,
                    "CASE",
                    expr_ctx,
                    signature=f"CASE {expr_ctx.getText()[:60]}",
                )
            return None

        def _visit_assert_step(self, ctx):
            text = _truncate(ctx.getText(), 80) if ctx.getText() else "ASSERT"
            self._append(StructuralElementKind.PROOF, "ASSERT", ctx, signature=text)
            return None

        # -- Helpers --

        def _extract_decl_name(self, item_ctx) -> str:
            if item_ctx.IDENTIFIER():
                return item_ctx.IDENTIFIER().getText()
            if item_ctx.prefixDecl():
                return item_ctx.prefixDecl().getText()
            if item_ctx.infixDecl():
                return item_ctx.infixDecl().getText()
            if item_ctx.postfixDecl():
                return item_ctx.postfixDecl().getText()
            return "?"

        def _extract_def_name(self, def_ctx) -> str | None:
            name = self._extract_name_from_children(def_ctx)
            if name and self._is_definition_name_valid(name):
                return name
            raw = def_ctx.getText().strip()
            if "==" in raw:
                lhs = raw.split("==", 1)[0].strip()
                if lhs.upper().startswith("LOCAL "):
                    lhs = lhs[6:].strip()
                token = lhs.split()[0] if lhs.split() else ""
                token = token.rstrip("(").rstrip(")").strip()
                if token and self._is_definition_name_valid(token):
                    return token
            return None

        def _build_signature(self, raw_lhs: str, name: str) -> str:
            if raw_lhs == name:
                return f"{name} == ..."

            # For function-style operators: name(params) or name(param1, param2)
            if ":" in raw_lhs:
                parts = raw_lhs.split(":", 1)
                params = parts[0].strip()
                if params:
                    return f"{name}({params}) == ..."
                return f"{name} == ..."

            # For infix operators, format with spaces around the operator
            if raw_lhs and raw_lhs != name and "\\" in name:
                # Try to format: a\opb -> a \op b
                # The name has double backslashes, raw_lhs has single backslashes
                name_single = name.replace("\\\\", "\\")
                if name_single in raw_lhs:
                    parts = raw_lhs.split(name_single, 1)
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip()
                        if left and right:
                            return f"{left} {name_single} {right} == ..."

            # For other operators, show the pattern
            if raw_lhs and raw_lhs != name:
                return f"{raw_lhs} == ..."

            return f"{name} == ..."

        def _raw_def_lhs(self, def_ctx) -> str:
            ident_lhs = def_ctx.identLhs()
            if ident_lhs:
                return ident_lhs.getText().strip()

            # Handle infix operators: a \op b
            infix_lhs = def_ctx.infixLhs()
            if infix_lhs:
                return infix_lhs.getText().strip()

            # Handle prefix operators: \op a
            prefix_lhs = def_ctx.prefixLhs()
            if prefix_lhs:
                return prefix_lhs.getText().strip()

            # Handle postfix operators: a \op
            postfix_lhs = def_ctx.postfixLhs()
            if postfix_lhs:
                return postfix_lhs.getText().strip()

            raw = def_ctx.getText().strip()
            if "==" in raw:
                lhs = raw.split("==", 1)[0].strip()
                if lhs.upper().startswith("LOCAL "):
                    lhs = lhs[6:].strip()
                return lhs
            return ""

        def _extract_name_from_children(self, def_ctx) -> str | None:
            ident_lhs = def_ctx.identLhs()
            if ident_lhs:
                name = self._scan_ident_lhs(ident_lhs)
                if name:
                    return name

            # Handle infix operators: a \op b
            infix_lhs = def_ctx.infixLhs()
            if infix_lhs:
                # Find the InfixOp child and extract the operator name
                for child in infix_lhs.getChildren():
                    if hasattr(child, "getRuleIndex") and "InfixOp" in type(child).__name__:
                        op_text = child.getText().strip()
                        if op_text:
                            return op_text

            # Handle prefix operators: \op a
            prefix_lhs = def_ctx.prefixLhs()
            if prefix_lhs:
                text = prefix_lhs.getText().strip()
                if text:
                    return text

            # Handle postfix operators: a \op
            postfix_lhs = def_ctx.postfixLhs()
            if postfix_lhs:
                text = postfix_lhs.getText().strip()
                if text:
                    return text

            return None

        def _scan_ident_lhs(self, ident_lhs) -> str | None:
            for child in ident_lhs.getChildren():
                txt = child.getText().strip()
                if txt and not txt.isspace():
                    name = txt.rstrip("(").rstrip(")").strip()
                    if name:
                        return name
            return None

        def _extract_func_def_name(self, func_ctx) -> str:
            if func_ctx.IDENTIFIER():
                return func_ctx.IDENTIFIER().getText()
            id_tuple = func_ctx.identifierTuple()
            if id_tuple and id_tuple.IDENTIFIER():
                idents = id_tuple.IDENTIFIER()
                if idents:
                    return idents[0].getText()
            return "?"

    return TlaplusStructureVisitor
