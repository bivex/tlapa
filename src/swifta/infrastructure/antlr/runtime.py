"""Shared ANTLR runtime helpers for TLA+ parsing."""

from __future__ import annotations

import importlib
from dataclasses import dataclass

from antlr4 import CommonTokenStream, InputStream
from antlr4.atn.PredictionMode import PredictionMode
from antlr4.error.ErrorStrategy import BailErrorStrategy
from antlr4.error.Errors import ParseCancellationException

from swifta.domain.errors import GeneratedParserNotAvailableError
from swifta.domain.model import GrammarVersion, SyntaxDiagnostic
from swifta.infrastructure.antlr.error_listener import CollectingErrorListener

ANTLR_GRAMMAR_VERSION = GrammarVersion(
    "antlr4@4.13.1+python:tlaplus/tla+ (converted from official JavaCC grammar)"
)

# TLA+ lexer mode constants (must match TLAPLusLexer.g4)
_SPEC_MODE = 1


@dataclass(frozen=True, slots=True)
class GeneratedParserTypes:
    lexer_type: type
    parser_type: type
    visitor_type: type


@dataclass(frozen=True, slots=True)
class ParseTreeResult:
    token_stream: CommonTokenStream
    parser: object
    tree: object
    diagnostics: tuple[SyntaxDiagnostic, ...]


def load_generated_types() -> GeneratedParserTypes:
    try:
        lexer_module = importlib.import_module(
            "swifta.infrastructure.antlr.generated.tlaplus.TLAPLusLexer"
        )
        parser_module = importlib.import_module(
            "swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParser"
        )
        visitor_module = importlib.import_module(
            "swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParserVisitor"
        )
    except ModuleNotFoundError as error:
        raise GeneratedParserNotAvailableError(
            "generated TLA+ parser artifacts are missing; run "
            "`uv run python scripts/generate_tlaplus_parser.py` first"
        ) from error

    return GeneratedParserTypes(
        lexer_type=lexer_module.TLAPLusLexer,
        parser_type=parser_module.TLAPLusParser,
        visitor_type=visitor_module.TLAPLusParserVisitor,
    )


def parse_source_text(
    source_text: str,
    generated_types: GeneratedParserTypes | None = None,
) -> ParseTreeResult:
    """Parse a complete TLA+ module (with ---- MODULE header)."""
    return _parse_entry_text(
        source_text,
        entry_rule_name="unit",
        generated_types=generated_types,
        force_spec_mode=False,
    )


def parse_expression_text(
    source_text: str,
    generated_types: GeneratedParserTypes | None = None,
) -> ParseTreeResult:
    """Parse a standalone TLA+ expression (no module header needed)."""
    return _parse_entry_text(
        source_text,
        entry_rule_name="expression",
        generated_types=generated_types,
        force_spec_mode=True,
    )


def parse_definition_text(
    source_text: str,
    generated_types: GeneratedParserTypes | None = None,
) -> ParseTreeResult:
    """Parse a TLA+ definition (no module header needed)."""
    return _parse_entry_text(
        source_text,
        entry_rule_name="operatorOrFunctionDefinition",
        generated_types=generated_types,
        force_spec_mode=True,
    )


def _parse_entry_text(
    source_text: str,
    *,
    entry_rule_name: str,
    generated_types: GeneratedParserTypes | None = None,
    force_spec_mode: bool = False,
) -> ParseTreeResult:
    generated = generated_types or load_generated_types()

    try:
        return _parse_entry_text_fast(source_text, generated, entry_rule_name, force_spec_mode)
    except ParseCancellationException:
        return _parse_entry_text_full(source_text, generated, entry_rule_name, force_spec_mode)


def _parse_entry_text_fast(
    source_text: str,
    generated: GeneratedParserTypes,
    entry_rule_name: str,
    force_spec_mode: bool,
) -> ParseTreeResult:
    lexer = generated.lexer_type(InputStream(source_text))
    if force_spec_mode:
        lexer.mode(_SPEC_MODE)

    lexer_errors = CollectingErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_errors)

    token_stream = CommonTokenStream(lexer)
    parser = generated.parser_type(token_stream)
    parser._interp.predictionMode = PredictionMode.SLL
    parser._errHandler = BailErrorStrategy()
    parser.removeErrorListeners()

    tree = getattr(parser, entry_rule_name)()
    token_stream.fill()

    return ParseTreeResult(
        token_stream=token_stream,
        parser=parser,
        tree=tree,
        diagnostics=tuple(lexer_errors.diagnostics),
    )


def _parse_entry_text_full(
    source_text: str,
    generated: GeneratedParserTypes,
    entry_rule_name: str,
    force_spec_mode: bool,
) -> ParseTreeResult:
    lexer = generated.lexer_type(InputStream(source_text))
    if force_spec_mode:
        lexer.mode(_SPEC_MODE)

    lexer_errors = CollectingErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_errors)

    token_stream = CommonTokenStream(lexer)
    parser = generated.parser_type(token_stream)
    parser_errors = CollectingErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(parser_errors)

    tree = getattr(parser, entry_rule_name)()
    token_stream.fill()

    return ParseTreeResult(
        token_stream=token_stream,
        parser=parser,
        tree=tree,
        diagnostics=tuple(lexer_errors.diagnostics + parser_errors.diagnostics),
    )
