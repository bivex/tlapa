import sys

sys.path.insert(0, "src")

from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusLexer import TLAPLusLexer
from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParser import TLAPLusParser
from antlr4 import CommonTokenStream, InputStream


def parse_file(path):
    with open(path, "r") as f:
        text = f.read()
    lexer = TLAPLusLexer(InputStream(text))
    tokens = CommonTokenStream(lexer)
    tokens.fill()
    parser = TLAPLusParser(tokens)
    parser.buildParseTrees = True
    tree = parser.unit()
    errs = parser.getNumberOfSyntaxErrors()
    return errs


if __name__ == "__main__":
    path = "example/distributed_log_full.tla"
    errs = parse_file(path)
    print(f"Syntax errors in {path}: {errs}")
    sys.exit(0 if errs == 0 else 1)
