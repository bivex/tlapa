import sys
sys.path.insert(0, 'src')

from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusLexer import TLAPLusLexer
from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParser import TLAPLusParser
from antlr4 import CommonTokenStream, InputStream


def dump_tokens(text):
    lexer = TLAPLusLexer(InputStream(text))
    tokens = CommonTokenStream(lexer)
    tokens.fill()
    for t in tokens.tokens:
        if t.type == -1:
            break
        name = lexer.symbolicNames[t.type] if t.type < len(lexer.symbolicNames) else f"?{t.type}"
        print(f"  {name:25s} '{t.text}' @L{t.line}:{t.column}")


def parse(label, text):
    lexer = TLAPLusLexer(InputStream(text))
    tokens = CommonTokenStream(lexer)
    tokens.fill()
    parser = TLAPLusParser(tokens)
    parser.buildParseTrees = True
    tree = parser.unit()
    errs = parser.getNumberOfSyntaxErrors()
    status = "OK" if errs == 0 else f"{ ERRS}"
    print(f"  [{status}] {label}")


print("=== Token dump: extends ===")
dump_tokens("---- MODULE M ----\nEXTENDS Naturals, FiniteSets\n====")

print("\n=== Token dump: conjunction ===")
dump_tokens("---- MODULE M ----\na == /\\ x = 1\n     /\\ y = 2\n====")

print("\n=== Token dump: inline conjunction ===")
dump_tokens("---- MODULE M ----\na == x /\\ y\n====")

print("\n=== Token dump: set diff ===")
dump_tokens("---- MODULE M ----\na == S \\ T\n====")

print("\n=== Token dump: notin ===")
dump_tokens("---- MODULE M ----\na == r \\notin allocated\n====")

print("\n=== Token dump: exists ===")
dump_tokens("---- MODULE M ----\na == \\E r \\in S : P(r)\n====")
