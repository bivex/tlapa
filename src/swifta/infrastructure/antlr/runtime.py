"""Shared ANTLR runtime helpers for TLA+ parsing."""

from __future__ import annotations

import hashlib
import importlib
from collections import OrderedDict
from dataclasses import dataclass

from antlr4 import CommonTokenStream, InputStream
from antlr4.atn.PredictionMode import PredictionMode
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy
from antlr4.error.Errors import ParseCancellationException

from swifta.domain.errors import GeneratedParserNotAvailableError
from swifta.domain.model import GrammarVersion, SyntaxDiagnostic
from swifta.infrastructure.antlr.error_listener import CollectingErrorListener

ANTLR_GRAMMAR_VERSION = GrammarVersion(
    "antlr4@4.13.1+python:tlaplus/tla+ (converted from official JavaCC grammar)"
)

_SPEC_MODE = 1

_DEFAULT_CACHE_MAX = 64


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


class ParseCache:
    """LRU cache for parse results keyed by content hash."""

    def __init__(self, maxsize: int = _DEFAULT_CACHE_MAX) -> None:
        self._maxsize = maxsize
        self._cache: OrderedDict[str, ParseTreeResult] = OrderedDict()

    def get(self, content: str, entry_rule: str) -> ParseTreeResult | None:
        key = self._make_key(content, entry_rule)
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, content: str, entry_rule: str, result: ParseTreeResult) -> None:
        key = self._make_key(content, entry_rule)
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._maxsize:
                self._cache.popitem(last=False)
        self._cache[key] = result

    def invalidate(self, content: str, entry_rule: str) -> None:
        key = self._make_key(content, entry_rule)
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)

    @staticmethod
    def _make_key(content: str, entry_rule: str) -> str:
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return f"{entry_rule}:{digest}"


_global_cache = ParseCache()


def get_global_cache() -> ParseCache:
    return _global_cache


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
    *,
    use_cache: bool = True,
) -> ParseTreeResult:
    """Parse a complete TLA+ module (with ---- MODULE header)."""
    return _parse_entry_text(
        source_text,
        entry_rule_name="unit",
        generated_types=generated_types,
        force_spec_mode=False,
        use_cache=use_cache,
    )


def parse_expression_text(
    source_text: str,
    generated_types: GeneratedParserTypes | None = None,
    *,
    use_cache: bool = True,
) -> ParseTreeResult:
    """Parse a standalone TLA+ expression (no module header needed)."""
    return _parse_entry_text(
        source_text,
        entry_rule_name="expression",
        generated_types=generated_types,
        force_spec_mode=True,
        use_cache=use_cache,
    )


def parse_definition_text(
    source_text: str,
    generated_types: GeneratedParserTypes | None = None,
    *,
    use_cache: bool = True,
) -> ParseTreeResult:
    """Parse a TLA+ definition (no module header needed)."""
    return _parse_entry_text(
        source_text,
        entry_rule_name="operatorOrFunctionDefinition",
        generated_types=generated_types,
        force_spec_mode=True,
        use_cache=use_cache,
    )


def _parse_entry_text(
    source_text: str,
    *,
    entry_rule_name: str,
    generated_types: GeneratedParserTypes | None = None,
    force_spec_mode: bool = False,
    use_cache: bool = True,
) -> ParseTreeResult:
    generated = generated_types or load_generated_types()

    cache = _global_cache if use_cache else None
    if cache is not None:
        cached = cache.get(source_text, entry_rule_name)
        if cached is not None:
            return cached

    try:
        result = _parse_entry_text_fast(source_text, generated, entry_rule_name, force_spec_mode)
    except ParseCancellationException:
        result = _parse_entry_text_full(source_text, generated, entry_rule_name, force_spec_mode)

    if cache is not None:
        cache.put(source_text, entry_rule_name, result)
    return result


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
    parser._errHandler = DefaultErrorStrategy()

    tree = getattr(parser, entry_rule_name)()
    token_stream.fill()

    return ParseTreeResult(
        token_stream=token_stream,
        parser=parser,
        tree=tree,
        diagnostics=tuple(lexer_errors.diagnostics + parser_errors.diagnostics),
    )
