# TLA+ Parser Roadmap

This document outlines the completion tasks for the TLA+ parser implementation built on ANTLR4.

## ✅ Completed

### Core Parser Infrastructure
- [x] Regenerate TLA+ lexer and parser from ANTLR4 grammar
- [x] Comment handling (line and block comments)
- [x] Basic expression parsing and structural element extraction
- [x] Dead code removal in parser adapter (unreachable strings, duplicate methods)

### Grammar Enhancements
- [x] **Bullet operators** (`/\`, `\/`) recognition at start of line
- [x] **Empty set literals** (`{}`) in set expressions
- [x] **BAR (`|`)** in function set comprehensions: `[x \in S | expr]`
- [x] **Prime support** in bound identifiers: `n' \in S`
- [x] Generalized **set comprehension** to accept any expressions after colon
- [x] **Record field syntax** with `|->` operator
- [x] **EXCEPT** expressions for record/function updates

### Grammar Bug Fixes
- [x] **Primed variable + function application**: Merged `applicationExpr` into `postfixExpr` so `logs'[node]` parses as `(logs')[node]` instead of just `logs'`
- [x] **Nested quantifiers with binary operators**: Changed right operands of `equivExpr`, `impliesExpr`, `orExpr`, and `andExpr` from next-lower-precedence rules to `quantifierExpr`, enabling `P => \A x: Q` and `P /\ \A x: Q`
- [x] **Action expressions `[A]_v`**: Added `LSB expression ARSB reducedExpression` alternative to `primaryExpression` for standalone action formulas (e.g., `[][Next]_<<vars>>`)
- [x] **Double-index EXCEPT**: `[voted_for EXCEPT ![node][msg.from] = TRUE]` works correctly
- [x] **fieldVal** accepts any expression as left side of `|->` (e.g., `[msg.last_log_index |-> ...]`)
- [x] **maybeBound rule**: Fixed `IN_KW` → `IN` so bounded CHOOSE (`CHOOSE x \in S : P(x)`) parses correctly

### Example Files
- [x] All 54 example TLA+ files parse without errors (was 48 OK / 6 FAIL)
- [x] Fixed invalid TLA+ in example files: `LET ... THEN` → `LET ... IN`, `UNCHANGED x, y` → `UNCHANGED <<x, y>>`, `\A idx > 0:` → `\A idx \in Nat: idx > 0 =>`, `\E x \subseteq S:` → `\E x \in SUBSET S:`, missing ELSE clauses, empty files

### HTML Generation
- [x] Nassi-Shneiderman diagram generation via CLI
- [x] SVG rendering with dark theme
- [x] Single file and directory batch processing
- [x] Index page generation for multi-file specs
- [x] Embedded Nassi diagrams in structural HTML (inline SVG after matching elements)
- [x] THEOREM and PROOF diagram support in Nassi builder
- [x] Proof step diagrams (HAVE, TAKE, WITNESS, PICK, CASE, ASSERT, QED, USE/HIDE, DEFINE)
- [x] **Premium Aesthetics**: SVG gradients, glow filters, and Tokyo Night color palette
- [x] **KaTeX Integration**: High-quality mathematical formula rendering for TLA+ symbols

### Grammar Completeness
- [x] Add support for temporal operators (`[]`, `<>`, `WF_`, `SF_`)
- [x] Complete proof syntax (BY, HAVE, QED, etc.)
- [x] Handle user-defined operator symbols correctly
- [x] Support for `LAMBDA` expressions
- [x] Full `CHOOSE` expression variants (bound/unbound)
- [x] `TAKE` and `WITNESS` constructs
- [x] `USE` and `HIDE` clauses

### Error Reporting
- [x] More precise error messages with TLA+-specific suggested fixes (22 hint patterns)
- [x] Error recovery to continue parsing after errors (SLL fast path + LL full path with DefaultErrorStrategy)
- [x] Warning level diagnostics (non-fatal issues) with false-positive classification
- [x] Source location tracking with line/column + end_line/end_column ranges

### Parser Adapter
- [x] Fix operator extraction after grammar changes
- [x] Remove dead code (unreachable strings after return, duplicate methods)
- [x] Handle all edge cases in operator signature extraction (infix, prefix, postfix)
- [x] Improve diagnostics for ill-formed specs
- [x] Proof/step visitors (visitProof, visitStep, visitQedStep, HAVE, TAKE, WITNESS, PICK, CASE, ASSERT)
- [x] Diagnostic classification with false-positive filtering

### Performance & Scalability
- [x] Parse result caching (LRU cache, SHA-256 hashing, configurable maxsize)

### Testing
- [x] 31 tests covering temporal operators, proof syntax, LAMBDA/CHOOSE, USE/HIDE, parse cache, error reporting, warning diagnostics, diagnostic DTOs

---

## ⏳ Future Milestones

### Performance & Scalability
- [ ] Incremental parsing for large specs
- [ ] Background parsing for IDE integration
- [ ] Memory usage optimization
- [ ] Performance benchmarks (<100ms for 500 lines)

### Tooling & Integration
- [ ] Language Server Protocol (LSP) support
- [ ] Syntax highlighting definitions (TextMate, VS Code)
- [ ] Test suite with 100+ TLA+ examples from community
- [ ] CI/CD validation against upstream grammar changes
- [ ] Docker container for reproducible builds

### Documentation
- [ ] Complete grammar documentation (what's supported, what's not)
- [ ] Migration guide from JavaCC grammar
- [ ] Performance tuning guide
- [ ] Contributing guidelines for grammar patches

---

## 🐛 Known Issues

- [x] **BY clause with multiple references**: `BY <1>, <2>` works correctly including bare levels
- [x] **Instantiation steps in proofs**: `instantiation` rule handled by NassiBuilder and structural visitor

---

## 📈 Success Criteria

- [x] All specs in `example/` directory parse without errors (54/54)
- [x] Nassi-Shneiderman diagrams generated for all operators
- [x] Parse result caching implemented
- [x] Error recovery with diagnostic collection
- [ ] 90%+ compatibility with TLA+ community specs (tlaplus/examples)
- [ ] Parse performance < 100ms for typical specs (500 lines)
- [ ] Zero crashes on malformed input (graceful error reporting)

---

## 🔗 References

- [TLA+ GitHub](https://github.com/tlaplus/tlaplus)
- [TLA+ Grammar (JavaCC)](https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/javacc/tla%2B.jj)
- [ANTLR Grammar Repository](https://github.com/antlr/grammars-v4/tree/master/tlaplus)
- [TLA+ Hyperbook](https://hyperbook.verif.net/)
- [Learn TLA+](https://learntla.com/)
