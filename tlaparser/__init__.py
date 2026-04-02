"""
TLA+ Parser - Python parser for TLA+ specifications.

Generated from an ANTLR4 grammar converted from the official TLA+ JavaCC grammar.
See: https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/javacc/tla%2B.jj
"""

from tlaparser.api import (
    parse_tla,
    parse_module,
    parse_expression,
    get_tokens,
    get_rule_names,
    get_token_names,
    TLAPLusLexer,
    TLAPLusParser,
    TLAPLusParserVisitor,
    TLAPLusParserListener,
    TLAErrorListener,
)

__all__ = [
    "parse_tla",
    "parse_module",
    "parse_expression",
    "get_tokens",
    "get_rule_names",
    "get_token_names",
]
