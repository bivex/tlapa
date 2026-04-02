import sys
sys.path.insert(0, 'src')

from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusLexer import TLAPLusLexer
from swifta.infrastructure.antlr.generated.tlaplus.TLAPLusParser import TLAPLusParser
from antlr4 import CommonTokenStream, InputStream


def parse(label, text):
    lexer = TLAPLusLexer(InputStream(text))
    tokens = CommonTokenStream(lexer)
    tokens.fill()
    parser = TLAPLusParser(tokens)
    parser.buildParseTrees = True
    tree = parser.unit()
    errs = parser.getNumberOfSyntaxErrors()
    status = "OK" if errs == 0 else f"{errs} ERRS"
    print(f"  [{status}] {label}")


# Test each construct in isolation
parse("minimal module", "---- MODULE M ----\n====")

parse("extends single", "---- MODULE M ----\nEXTENDS Naturals\n====")

parse("extends two", "---- MODULE M ----\nEXTENDS Naturals, FiniteSets\n====")

parse("extends three", "---- MODULE M ----\nEXTENDS Naturals, Integers, FiniteSets\n====")

parse("variable single", "---- MODULE M ----\nVARIABLE x\n====")

parse("variable multi", "---- MODULE M ----\nVARIABLES x, y\n====")

parse("constant single", "---- MODULE M ----\nCONSTANT C\n====")

parse("constant multi", "---- MODULE M ----\nCONSTANTS A, B\n====")

parse("simple def", "---- MODULE M ----\na == 1\n====")

parse("def equals expr", "---- MODULE M ----\na == x = y\n====")

parse("def conjunction", "---- MODULE M ----\na == /\\ x = 1\n     /\\ y = 2\n====")

parse("def disjunction", "---- MODULE M ----\na == \\/ x = 1\n     \\/ y = 2\n====")

parse("def empty set", "---- MODULE M ----\na == {}\n====")

parse("def set enum", "---- MODULE M ----\na == {1, 2, 3}\n====")

parse("def set of", "---- MODULE M ----\na == {x \\in S : P(x)}\n====")

parse("def exists", "---- MODULE M ----\na == \\E x \\in S : P(x)\n====")

parse("def forall", "---- MODULE M ----\na == \\A x \\in S : P(x)\n====")

parse("def primed", "---- MODULE M ----\na == x'\n====")

parse("def cup", "---- MODULE M ----\na == x \\cup y\n====")

parse("def minus set", "---- MODULE M ----\na == x \\ y\n====")

parse("allocator init", """---- MODULE M ----
VARIABLES allocated, requests
Init ==
    /\\ allocated = {}
    /\\ requests = {}
Next == allocated' = allocated
Spec == Init /\\ [][Next]_<<allocated, requests>>
====""")

parse("allocator full", """---- MODULE M ----
EXTENDS Naturals, FiniteSets
CONSTANTS Clients, Resources
VARIABLES allocated, requests
TypeInvariant ==
    /\\ allocated \\subseteq Resources
    /\\ requests \\subseteq Resources
Init ==
    /\\ allocated = {}
    /\\ requests = {}
Request(c) ==
    /\\ \\E r \\in Resources \\ allocated :
        requests' = requests \\cup {r}
    /\\ allocated' = allocated
Allocate(c, r) ==
    /\\ r \\in requests
    /\\ r \\notin allocated
    /\\ allocated' = allocated \\cup {r}
    /\\ requests' = requests \\ {r}
Release(c, r) ==
    /\\ r \\in allocated
    /\\ allocated' = allocated \\ {r}
    /\\ requests' = requests
Next ==
    \\E c \\in Clients :
        \\/ Request(c)
        \\/ \\E r \\in Resources : Allocate(c, r) \\/ Release(c, r)
Spec == Init /\\ [][Next]_<<allocated, requests>>
NoDeadlock == ~(allocated = Resources /\\ requests = {})
====""")
