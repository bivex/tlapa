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
            self._module_name: str | None = None

        # -- Module-level constructs --

        def visitFirstModule(self, ctx):
            # Extract module name (first IDENTIFIER after SEPARATOR)
            if ctx.IDENTIFIER():
                self._module_name = ctx.IDENTIFIER().getText()
                self._append(StructuralElementKind.MODULE, self._module_name, ctx)
            # Visit body children explicitly
            body = ctx.moduleBody()
            if body:
                for child in body.getChildren():
                    self.visit(child)
            return None

        def visitModule(self, ctx):
            # Subsequent modules (SEPARATOR IDENTIFIER SEPARATOR ...)
            if ctx.IDENTIFIER():
                self._module_name = ctx.IDENTIFIER().getText()
                self._append(StructuralElementKind.MODULE, self._module_name, ctx)
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
            self._append(
                StructuralElementKind.OPERATOR_DEFINITION,
                name,
                ctx,
                signature=f"{name} == ...",
            )
            return None

        def visitFunctionDefinition(self, ctx):
            name = self._extract_func_def_name(ctx)
            self._append(
                StructuralElementKind.FUNCTION_DEFINITION,
                name,
                ctx,
                signature=f"{name}[...] == ...",
            )
            return None

        def visitModuleDefinition(self, ctx):
            ident = ctx.IDENTIFIER()
            name = ident.getText() if ident else "module_def"
            self._append(
                StructuralElementKind.MODULE_DEFINITION,
                name,
                ctx,
                signature=f"{name} == ...",
            )
            return None

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

        def _extract_def_name(self, def_ctx) -> str:
            ident_lhs = def_ctx.identLhs()
            if ident_lhs and ident_lhs.IDENTIFIER():
                return ident_lhs.IDENTIFIER().getText()
            prefix_lhs = def_ctx.prefixLhs()
            if prefix_lhs:
                return prefix_lhs.getText()
            infix_lhs = def_ctx.infixLhs()
            if infix_lhs:
                return infix_lhs.getText()
            postfix_lhs = def_ctx.postfixLhs()
            if postfix_lhs:
                return postfix_lhs.getText()
            return "?"

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
