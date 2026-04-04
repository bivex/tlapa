import sys

sys.path.insert(0, "src")

from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusLexer import TLAPLusLexer
from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParser import TLAPLusParser
from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener


class ErrorCollector(ErrorListener):
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append((line, column, msg))


def parse_file(path):
    with open(path, "r") as f:
        text = f.read()
    lexer = TLAPLusLexer(InputStream(text))
    tokens = CommonTokenStream(lexer)
    tokens.fill()
    parser = TLAPLusParser(tokens)
    parser.removeErrorListeners()
    error_listener = ErrorCollector()
    parser.addErrorListener(error_listener)
    parser.buildParseTrees = True
    tree = parser.unit()
    return len(error_listener.errors), error_listener.errors


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "example/distributed_log_full.tla"
    errs, details = parse_file(path)
    print(f"Total syntax errors: {errs}")
    for line, col, msg in details:
        print(f"Line {line}:{col} - {msg}")
