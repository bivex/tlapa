"""
TLA+ Parser - Python parser for TLA+ specifications.

This module provides a high-level API for parsing TLA+ specifications
using a parser generated from an ANTLR4 grammar that was converted from
the official TLA+ JavaCC grammar.

Usage:
    from tlaparser import parse_tla, parse_expression

    # Parse a complete TLA+ module
    tree = parse_tla('''
    ---- MODULE Test ----
    EXTENDS Naturals
    x == 1 + 2
    ====
    ''')

    # Parse a standalone expression
    expr = parse_expression('x + y * 3')
"""

import sys
import os

# Add the parser directory to the path so we can import the generated modules
_parser_dir = os.path.join(os.path.dirname(__file__), "parser")
if _parser_dir not in sys.path:
    sys.path.insert(0, _parser_dir)

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from tlaparser.parser.TLAPLusLexer import TLAPLusLexer
from tlaparser.parser.TLAPLusParser import TLAPLusParser
from tlaparser.parser.TLAPLusParserVisitor import TLAPLusParserVisitor
from tlaparser.parser.TLAPLusParserListener import TLAPLusParserListener


class TLAErrorListener(ErrorListener):
    """Collects syntax errors during parsing."""

    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(
            {
                "line": line,
                "column": column,
                "message": msg,
                "offending_symbol": offendingSymbol,
            }
        )


def parse_tla(source: str, start_rule: str = "unit") -> TLAPLusParser:
    """
    Parse a TLA+ source string.

    Args:
        source: TLA+ source code string.
        start_rule: The parser rule to start from. Default is 'unit' (complete module).
                    Other useful values: 'module', 'expression', 'operatorOrFunctionDefinition'.

    Returns:
        The parser object. Use parser.getParseTree() or access parser.<start_rule>()
        to get the parse tree. Check parser.errors for any syntax errors.

    Raises:
        ValueError: If the start_rule is not a valid parser rule.
    """
    input_stream = InputStream(source)
    lexer = TLAPLusLexer(input_stream)

    # If we're not parsing a full module (unit), start in SPEC mode
    # so the lexer doesn't skip everything in DEFAULT mode
    if start_rule != "unit":
        lexer.mode(TLAPLusLexer.SPEC_MODE)

    token_stream = CommonTokenStream(lexer)
    parser = TLAPLusParser(token_stream)

    # Attach error listener
    error_listener = TLAErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    # Parse using the requested start rule
    if not hasattr(parser, start_rule):
        raise ValueError(f"Unknown parser rule: {start_rule}")

    rule_method = getattr(parser, start_rule)
    tree = rule_method()

    # Store errors on the tree for later inspection
    tree._errors = error_listener.errors
    tree._parser = parser
    tree._lexer = lexer

    return tree


def parse_module(source: str):
    """Parse a TLA+ module (without the enclosing SEPARATOR...MODULE header)."""
    return parse_tla(source, "module")


def parse_expression(source: str):
    """Parse a standalone TLA+ expression."""
    return parse_tla(source, "expression")


def get_tokens(source: str):
    """
    Tokenize a TLA+ source string and return the list of tokens.

    Returns:
        List of dicts with 'type', 'text', 'line', 'column', 'index' keys.
    """
    input_stream = InputStream(source)
    lexer = TLAPLusLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()

    tokens = []
    for token in token_stream.tokens:
        if token.type == -1:  # EOF
            continue
        tokens.append(
            {
                "type": lexer.symbolicNames[token.type]
                if token.type < len(lexer.symbolicNames)
                else f"TYPE_{token.type}",
                "text": token.text,
                "line": token.line,
                "column": token.column,
                "index": token.tokenIndex,
            }
        )
    return tokens


def get_rule_names():
    """Return the list of all parser rule names."""
    return list(TLAPLusParser.ruleNames)


def get_token_names():
    """Return the list of all lexer token names."""
    lexer = TLAPLusLexer(InputStream(""))
    return list(lexer.symbolicNames)


__all__ = [
    "parse_tla",
    "parse_module",
    "parse_expression",
    "get_tokens",
    "get_rule_names",
    "get_token_names",
    "TLAPLusLexer",
    "TLAPLusParser",
    "TLAPLusParserVisitor",
    "TLAPLusParserListener",
    "TLAErrorListener",
]
