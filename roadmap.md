# TLA+ Parser Roadmap

This document outlines the completion tasks for the TLA+ parser implementation built on ANTLR4.

## ✅ Completed

### Core Parser Infrastructure
- [x] Regenerate TLA+ lexer and parser from ANTLR4 grammar
- [x] Comment handling (line and block comments)
- [x] Basic expression parsing and structural element extraction

### Grammar Enhancements
- [x] **Bullet operators** (`/\`, `\/`) recognition at start of line
- [x] **Empty set literals** (`{}`) in set expressions
- [x] **BAR (`|`)** in function set comprehensions: `[x \in S | expr]`
- [x] **Prime support** in bound identifiers: `n' \in S`
- [x] Generalized **set comprehension** to accept any expressions after colon
- [x] **Record field syntax** with `|->` operator
- [x] **EXCEPT** expressions for record/function updates

### HTML Generation
- [x] Nassi-Shneiderman diagram generation via CLI
- [x] SVG rendering with dark theme
- [x] Single file and directory batch processing
- [x] Index page generation for multi-file specs

---

## 🔄 In Progress / Partially Done

### Parser Adapter
- [ ] ~~Fix operator extraction after grammar changes~~ (mostly working)
- [ ] Handle all edge cases in operator signature extraction
- [ ] Improve diagnostics for ill-formed specs

### Full Spec Compatibility
- [ ] Resolve remaining syntax errors in `distributed_log_full.tla` (8 diagnostics)
  - Issues with nested EXCEPT indexing: `voted_for' = [voted_for EXCEPT ![node][msg.from] = TRUE]`
  - IF/THEN/ELSE combinations inside EXCEPT contexts
  - Potential need for grammar adjustments for complex EXCEPT patterns

---

## ⏳ Future Milestones

### Grammar Completeness
- [ ] Add support for temporal operators (`[]`, `<>`, `WF_`, `SF_`)
- [ ] Complete proof syntax (BY, HAVE, QED, etc.)
- [ ] Handle user-defined operator symbols correctly
- [ ] Support for `LAMBDA` expressions
- [ ] Full `CHOOSE` expression variants
- [ ] `TAKE` and `WITNESS` constructs
- [ ] `USE` and `HIDE` clauses

### Error Reporting
- [ ] More precise error messages with suggested fixes
- [ ] Error recovery to continue parsing after errors
- [ ] Warning level diagnostics (non-fatal issues)
- [ ] Source location tracking with proper line/column

### Performance & Scalability
- [ ] Incremental parsing for large specs
- [ ] Parse result caching
- [ ] Background parsing for IDE integration
- [ ] Memory usage optimization

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

1. **EXCEPT double-indexing**  
   `voted_for' = [voted_for EXCEPT ![node][msg.from] = TRUE]` fails to parse  
   Likely grammar rule missing for multi-level EXCEPT chaining.

2. **IF/ELSE inside EXCEPT contexts**  
   Complex conditional updates with primes and indexing cause parse failures.

3. **Operator signature extraction**  
   Some operators with primes or unusual LHS forms not properly detected.

4. **Comment handling**  
   Block comments inside expressions may interfere with token stream.

---

## 📈 Success Criteria

- [ ] All specs in `example/` directory parse without errors
- [ ] Nassi-Shneiderman diagrams generated for all operators
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
