# tlapa

tlapa is a simple, scalable monolith for parsing TLA+ source code through ANTLR while keeping the architecture clean enough for future semantic analysis, indexing, and export pipelines.

The project starts from the domain, not from the framework:

* business goal: convert TLA+ source into a stable structural model for downstream tooling
* architectural style: DDD-inspired layered monolith with hexagonal boundaries
* parser engine: ANTLR4 with a comprehensive TLA+ grammar supporting operators, temporal logic, and proofs
* current delivery channels: CLI for parsing, HTML structure diagrams, Nassi-Shneiderman control flow visualization

## What the system does

Today the system supports:

* **Parsing TLA+ code**
  * parsing one TLA+ file
  * parsing a directory of TLA+ files
  * extracting a lightweight structural model: modules, variables, constants, operators, functions, instantiations, proofs, and theorems
  * reporting syntax diagnostics with precise line/column information
  * tracking grammar version and parsing statistics

* **Structural analysis**
  * TLA+ operator definitions (`==`, `\equiv`)
  * function definitions (`[x \in S |-> e]`)
  * quantifiers (`\A`, `\E`)
  * temporal operators (`[]`, `<>`, `WF`, `SF`)
  * proof infrastructures (`PROOF`, `QED`, `HAVE`, `BY`, `OBVIOUS`, `ASSERT`, `TAKE`, `WITNESS`)
  * set expressions, function sets, records, EXCEPT expressions

* **Nassi-Shneiderman diagrams for proofs and operators**
  * building a Nassi-Shneiderman HTML diagram for one TLA+ file
  * classic NS rendering for structured operator bodies and proof steps
  * color-coded block types (operators, proofs, assumptions, theorems)
  * depth badges for nested proof structures (up to 50 levels)
  * dark Tokyo Night-inspired theme with JetBrains Mono font
  * responsive layout

* **Architecture**
  * keeping parser infrastructure behind ports so the application layer stays independent from ANTLR, filesystem, and CLI details
  * immutable domain model with value objects
  * event-driven internal communication
  * clear separation: domain → application → infrastructure → presentation

## Diagram features

The Nassi-Shneiderman diagrams include:

* **Visual clarity**
  * Classic NS rectangles for operator bodies and proof steps
  * Color-coded block types (operators=teal, proofs=blue, assumptions=red, theorems=red, uses=green)
  * Icons for quick recognition (≜ for operators, 📝 for proofs, etc.)
  * Line numbers for source traceability

* **Structure-first rendering**
  * Operators and proofs rendered with signature summaries
  * Nested subblocks for `IF`, `CASE`, `\E`, quantifier scopes
  * Minimalist blocks for `USE`, `HIDE` declarations

* **Dark theme**
  * Tokyo Night-inspired color palette optimized for readability
  * Surface and border tokens for clear hierarchy

* **Smart parsing**
  * Fast path for simple operator definitions
  * Graceful handling of partially parsed constructs (diagnostics shown, parsing continues)

## Architecture

The codebase is split into four explicit layers:

* `domain`: domain model (SourceUnit, StructuralElement, Diagnostic), invariants, ports, events
* `application`: use cases (ParseFile, ParseDirectory, BuildDiagram) and DTOs
* `infrastructure`: ANTLR adapter, filesystem adapters, event publishing, generated grammars
* `presentation`: CLI commands and HTML renderers

See the full design docs in `docs/` (to be created).

## Quick start

1. Install dependencies:

```bash
uv sync --extra dev
```

2. Parse a single TLA+ file:

```bash
uv run tlapa parse-file example/tutorials/feature_tour.tla
```

3. Parse a directory:

```bash
uv run tlapa parse-dir tests/fixtures
```

4. Generate a structure HTML page (element breakdown + diagnostics):

```bash
uv run tlapa structure-file example/tutorials/feature_tour.tla --out output/feature_tour.structure.html
```

5. Generate Nassi-Shneiderman diagram for an operator/proof:

```bash
uv run tlapa nassi-file example/tutorials/feature_tour.tla --out output/feature_tour.nassi.html
```

6. Build diagrams for an entire directory:

```bash
uv run tlapa nassi-dir tests/fixtures --out output/nassi-bundle
```

## Project layout

```
tlapa/
├── src/swifta/           # Python packages (domain, application, infrastructure, presentation)
├── example/
│   ├── tutorials/        # beginner-friendly specs (feature_tour.tla, simple_distributed.tla)
│   ├── raft/             # Raft-related specs (distributed_log_full.tla, etc.)
│   └── advanced/         # large/complex specs and generated HTML
├── tests/
│   ├── fixtures/         # organized test specs
│   │   ├── operators/    # operator-stress tests
│   │   ├── proofs/       # proof syntax tests
│   │   ├── temporal/     # temporal logic tests
│   │   ├── integration/  # full-module integration tests
│   │   ├── grammar/      # grammar corner cases
│   │   └── minimal/      # tiny spec fragments
│   └── test_*.py         # pytest suite
├── scripts/
│   ├── gen_nassi_html.py # standalone diagram generator
│   └── debug/            # development utilities
├── docs/                 # design documentation (ADRs, diagrams)
└── tools/                # auxiliary scripts
```

## Constraints and honesty

The ANTLR grammar is hand-maintained and aims for TLA+ standard syntax as described in *Specifying Systems* and the TLA+ reference documentation. Some advanced patterns (e.g., function set constructors `[A -> B]` in certain infix contexts, deeply nested EXCEPT) may trigger false positives. Mutation testing (`scripts/mutation/mutation_diagnostics.py`) is used to ensure diagnostics catch real mistakes.

## Next steps

Useful future extensions:

* richer structural element extraction ( invariants, actions, subactions )
* semantic analysis (type inference, unused variable detection)
* TLC configuration parsing and model checking integration
* export to DOT/Graphviz for dependency graphs
* interactive diagrams with collapsible nodes and navigation
* language server protocol (LSP) support
* support for PlusCal translation and analysis
