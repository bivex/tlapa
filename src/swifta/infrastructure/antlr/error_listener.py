"""ANTLR error listener adapters."""

from __future__ import annotations

import re

from antlr4.error.ErrorListener import ErrorListener

from swifta.domain.model import DiagnosticSeverity, SyntaxDiagnostic

_TLA_FIXES: list[tuple[str, str, str]] = [
    (
        r"mismatched input '(\w+)' expecting",
        "did you mean to use '\\%s' as an operator?",
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
        "backslash operators must be followed by a keyword (e.g., \\in, \\E, \\A)",
        "backslash",
    ),
    (
        r"mismatched input '=' expecting DEF",
        "use '==' for operator definitions, not '='",
        "definition",
    ),
    (
        r"extraneous input '=' expecting",
        "operator definitions should use '==', not '='",
        "definition",
    ),
    (
        r"mismatched input 'IF'",
        "IF-THEN-ELSE requires THEN and ELSE branches: IF cond THEN a ELSE b",
        "if_then_else",
    ),
    (
        r"mismatched input 'THEN'",
        "THEN must follow the condition in IF-THEN-ELSE",
        "if_then_else",
    ),
    (
        r"mismatched input 'ELSE'",
        "ELSE must follow the THEN branch in IF-THEN-ELSE",
        "if_then_else",
    ),
    (
        r"mismatched input 'LET'",
        "LET-IN expressions require: LET def == ... IN expr",
        "let_in",
    ),
    (
        r"missing 'IN'",
        "LET-IN expression is missing the IN keyword",
        "let_in",
    ),
    (
        r"missing 'THEN'",
        "IF-THEN-ELSE is missing THEN after the condition",
        "if_then_else",
    ),
    (
        r"missing 'ELSE'",
        "IF-THEN-ELSE is missing ELSE after the THEN branch",
        "if_then_else",
    ),
    (
        r"token recognition error at: '=='",
        "use '==' for definitions (two equal signs)",
        "definition",
    ),
    (
        r"missing SEPARATOR",
        "module body must follow the module header '---- MODULE Name ----'",
        "begin_module",
    ),
    (r"expecting", "unexpected token; check operator spelling and TLA+ syntax", "syntax"),
]


class CollectingErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.diagnostics: list[SyntaxDiagnostic] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        enhanced = _enhance_message(msg)
        end_line = line
        end_column = column
        if offendingSymbol and hasattr(offendingSymbol, "stop"):
            try:
                stop = offendingSymbol.stop
                if stop is not None and hasattr(stop, "line"):
                    end_line = stop.line if hasattr(stop, "line") else line
                    end_column = (stop.column + 1) if hasattr(stop, "column") else column
            except (AttributeError, TypeError):
                pass
        elif offendingSymbol and hasattr(offendingSymbol, "text"):
            text_len = len(offendingSymbol.text) if offendingSymbol.text else 1
            end_line = line
            end_column = column + text_len
        self.diagnostics.append(
            SyntaxDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                message=enhanced,
                line=line,
                column=column,
                end_line=end_line,
                end_column=end_column,
            )
        )


class WarningCollectingListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.diagnostics: list[SyntaxDiagnostic] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        end_line = line
        end_column = column
        if offendingSymbol and hasattr(offendingSymbol, "text"):
            text_len = len(offendingSymbol.text) if offendingSymbol.text else 1
            end_column = column + text_len
        self.diagnostics.append(
            SyntaxDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                message=msg,
                line=line,
                column=column,
                end_line=end_line,
                end_column=end_column,
            )
        )


def _enhance_message(message: str) -> str:
    for pattern, fix, _tag in _TLA_FIXES:
        if re.search(pattern, message, re.IGNORECASE):
            return f"{message} (hint: {fix})"
    return message


def format_diagnostic(diag: SyntaxDiagnostic, source_lines: list[str] | None = None) -> str:
    loc = f"L{diag.line}:{diag.column}"
    if diag.end_line and diag.end_line != diag.line:
        loc += f"-L{diag.end_line}:{diag.end_column}"
    elif diag.end_column and diag.end_column != diag.column:
        loc += f"-{diag.end_column}"
    sev = diag.severity.value.upper()
    msg = diag.message
    ctx = ""
    if source_lines and 0 < diag.line <= len(source_lines):
        line_text = source_lines[diag.line - 1].rstrip()
        caret = " " * diag.column + "^"
        ctx = f"\n  {line_text}\n  {caret}"
    return f"{sev} {loc}: {msg}{ctx}"
