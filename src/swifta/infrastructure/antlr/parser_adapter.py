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
)
from swifta.domain.ports import TlaplusSyntaxParser
from swifta.infrastructure.antlr.runtime import (
    ANTLR_GRAMMAR_VERSION,
    load_generated_types,
    parse_source_text,
)


class AntlrTlaplusSyntaxParser(TlaplusSyntaxParser):
    def __init__(self) -> None:
        self._generated = load_generated_types()

    @property
    def grammar_version(self) -> GrammarVersion:
        return ANTLR_GRAMMAR_VERSION

    def parse(self, source_unit: SourceUnit) -> ParseOutcome:
        started_at = perf_counter()
        try:
            parse_result = parse_source_text(source_unit.content, self._generated)
            visitor = _build_structure_visitor(self._generated.visitor_type)()
            visitor.visit(parse_result.tree)

            elements = tuple(visitor.elements)
            elapsed_ms = round((perf_counter() - started_at) * 1000, 3)

            return ParseOutcome.success(
                source_unit=source_unit,
                grammar_version=self.grammar_version,
                diagnostics=parse_result.diagnostics,
                structural_elements=elements,
                statistics=ParseStatistics(
                    token_count=len(parse_result.token_stream.tokens),
                    structural_element_count=len(elements),
                    diagnostic_count=len(parse_result.diagnostics),
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


def _build_structure_visitor(visitor_base: type) -> type:
    """Build a visitor that walks the TLA+ parse tree and extracts structural elements."""

    class TlaplusStructureVisitor(visitor_base):
        def __init__(self) -> None:
            super().__init__()
            self.elements: list[StructuralElement] = []
            self._contexts: list[tuple[StructuralElement, object]] = []
            self._module_name: str | None = None

        def get_context(self, element: StructuralElement) -> object | None:
            for e, ctx in self._contexts:
                if e is element:
                    return ctx
            return None

        # -- Module-level constructs --

        def visitFirstModule(self, ctx):
            # Extract module name from the beginModule child; require proper header with SEPARATOR '----'
            bm = ctx.beginModule()
            if not bm:
                return None
            sep_tok = bm.SEPARATOR()
            if not sep_tok or sep_tok.getText() != "----":
                return None
            ident = bm.IDENTIFIER()
            if ident:
                name = ident.getText()
                self._module_name = name
                self._append(StructuralElementKind.MODULE, name, ctx)
            # Visit body children explicitly
            body = ctx.moduleBody()
            if body:
                for child in body.getChildren():
                    self.visit(child)
            return None

        def visitModule(self, ctx):
            # Subsequent modules; same header check
            bm = ctx.beginModule()
            if not bm:
                return None
            sep_tok = bm.SEPARATOR()
            if not sep_tok or sep_tok.getText() != "----":
                return None
            ident = bm.IDENTIFIER()
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
            names = [ident.getText() for ident in ctx.IDENTIFIER()]
            for name in names:
                self._append(StructuralElementKind.EXTENDS, name, ctx)
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
            # Preserve raw LHS text for better classification (e.g., primed variables indicate actions)
            raw_lhs = self._raw_def_lhs(ctx)
            signature = f"{raw_lhs} == ..." if raw_lhs else f"{name} == ..."
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
            # ModuleDefinition is rarely used in typical TLA+; parser often confuses expressions
            # with module definitions. Skip to reduce noise in structure diagrams.
            return None

        def _is_definition_name_valid(self, name: str) -> bool:
            """Validate definition names to filter out parse artifacts."""
            if not name or " " in name:
                return False
            # Backslash operators (e.g., \in, \cup, \subseteq) — only pure backslash+letters allowed
            if name.startswith("\\"):
                after = name[1:]
                return after.isalpha() and len(name) <= 12
            # Standard identifiers: alphanumeric, underscore, dot (for container-qualified)
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

        def visitProof(self, ctx):
            self._append(
                StructuralElementKind.PROOF,
                "PROOF",
                ctx,
            )
            return self.visitChildren(ctx)

        def visitUseOrHide(self, ctx):
            kind = StructuralElementKind.USE if ctx.USE_KW() else StructuralElementKind.HIDE
            self._append(kind, ctx.getText()[:40], ctx)
            return None

        # -- Helpers --

        def _append(self, kind, name: str, ctx, signature: str | None = None) -> None:
            container = self._module_name
            line = ctx.start.line if hasattr(ctx, "start") and ctx.start else 0
            column = ctx.start.column if hasattr(ctx, "start") and ctx.start else 0
            self.elements.append(
                StructuralElement(
                    kind=kind,
                    name=name,
                    line=line,
                    column=column,
                    container=container,
                    signature=signature,
                )
            )

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
            """Extract operator/function name from definition context, handling TLA+ operator symbols."""
            # Primary extraction from parse tree children
            name = self._extract_name_from_children(def_ctx)
            if name and self._is_definition_name_valid(name):
                return name
            # Fallback: parse raw text before '=='
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

            """Return raw left-hand side text of definition (including any primes, operators)."""
            # Try identLhs first
            ident_lhs = def_ctx.identLhs()
            if ident_lhs:
                return ident_lhs.getText().strip()
            # Check prefix/infix/postfix
            for attr in ("prefixLhs", "infixLhs", "postfixLhs"):
                lhs = getattr(def_ctx, attr)()
                if lhs:
                    text = lhs.getText().strip()
                    if text:
                        return text
            # Fallback: parse raw text before '=='
            raw = def_ctx.getText().strip()
            if "==" in raw:
                lhs = raw.split("==", 1)[0].strip()
                if lhs.upper().startswith("LOCAL "):
                    lhs = lhs[6:].strip()
                return lhs
            return ""

        def _raw_def_lhs(self, def_ctx) -> str:
            """Return raw left-hand side text of definition (including any primes, operators)."""
            # Try identLhs first
            ident_lhs = def_ctx.identLhs()
            if ident_lhs:
                return ident_lhs.getText().strip()
            # Check prefix/infix/postfix
            for attr in ("prefixLhs", "infixLhs", "postfixLhs"):
                lhs = getattr(def_ctx, attr)()
                if lhs:
                    text = lhs.getText().strip()
                    if text:
                        return text
            # Fallback: parse raw text before '=='
            raw = def_ctx.getText().strip()
            if "==" in raw:
                lhs = raw.split("==", 1)[0].strip()
                if lhs.upper().startswith("LOCAL "):
                    lhs = lhs[6:].strip()
                return lhs
            return ""

        def _extract_name_from_children(self, def_ctx) -> str | None:
            """Try to extract name from identLhs, prefixLhs, infixLhs, postfixLhs."""
            ident_lhs = def_ctx.identLhs()
            if ident_lhs:
                name = self._scan_ident_lhs(ident_lhs)
                if name:
                    return name
            for attr in ("prefixLhs", "infixLhs", "postfixLhs"):
                lhs = getattr(def_ctx, attr)()
                if lhs:
                    text = lhs.getText().strip()
                    if text:
                        token = text.split()[0] if text.split() else None
                        if token:
                            token = token.rstrip("(").rstrip(")").strip()
                            if token:
                                return token
            return None

        def _extract_name_from_children(self, def_ctx) -> str | None:
            """Try to extract name from identLhs, prefixLhs, infixLhs, postfixLhs."""
            ident_lhs = def_ctx.identLhs()
            if ident_lhs:
                name = self._scan_ident_lhs(ident_lhs)
                if name:
                    return name
            for attr in ("prefixLhs", "infixLhs", "postfixLhs"):
                lhs = getattr(def_ctx, attr)()
                if lhs:
                    text = lhs.getText().strip()
                    if text:
                        token = text.split()[0] if text.split() else None
                        if token:
                            token = token.rstrip("(").rstrip(")").strip()
                            if token:
                                return token
            return None

        def _scan_ident_lhs(self, ident_lhs) -> str | None:
            """Scan identLhs children to find the operator token."""
            # identLhs can be: IDENTIFIER | prefixOp | infixOp | postfixOp
            # Look for any child that returns meaningful text
            for child in ident_lhs.getChildren():
                txt = child.getText().strip()
                if txt and not txt.isspace():
                    # Remove trailing parens if present
                    name = txt.rstrip("(").rstrip(")").strip()
                    if name:
                        return name
            return None

        def _extract_name_from_text(self, text: str) -> str | None:
            """Extract name from raw text, handling TLA+ operator syntax."""
            if not text:
                return None
            # Split on whitespace and take first token
            tokens = text.split()
            if not tokens:
                return None
            first = tokens[0]
            # Remove trailing '=' or '(' if present
            first = first.rstrip("=").rstrip("(").strip()
            if not first:
                return None
            return first

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
