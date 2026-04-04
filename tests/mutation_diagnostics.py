#!/usr/bin/env python3
"""
Mutation testing for TLA+ parser diagnostics — detailed analysis.

Runs mutations and prints which ones produce same diagnostic count (potential blind spots).
"""

import argparse
import random
import string
from pathlib import Path
from typing import List, Tuple

from swifta.infrastructure.antlr.parser_adapter import AntlrTlaplusSyntaxParser
from swifta.domain.model import SourceUnit, SourceUnitId


def parse_content(content: str) -> Tuple[int, List[str]]:
    parser = AntlrTlaplusSyntaxParser()
    source_unit = SourceUnit(
        identifier=SourceUnitId("mut"),
        location="mut.tla",
        content=content,
    )
    outcome = parser.parse(source_unit)
    messages = [f"L{d.line}:{d.column} {d.message}" for d in outcome.diagnostics]
    return len(outcome.diagnostics), messages


def insert_char(content: str, pos: int, new_char: str) -> str:
    return content[:pos] + new_char + content[pos:]


def delete_char(content: str, pos: int) -> str:
    return content[:pos] + content[pos + 1 :]


def generate_mutations(content: str) -> List[Tuple[str, str]]:
    mutations = []
    # Common keyword and operator substitutions
    patterns = [
        ("PROOF", "PROOF BY"),
        ("PROOF BY", "PROOF"),
        ("PROOF OBVIOUS", "PROOF"),
        ("PROOF", "PROOF OBVIOUS"),
        ("QED", "QED OBVIOUS"),
        ("HAVE", "HAVE BY"),
        ("BY", "BY OBVIOUS"),
        ("\\in", "\\in \\in"),
        ("\\A", "\\A \\E"),
        ("\\E", "\\E \\A"),
        ("/\\", "/\\ /\\"),
        ("\\/", "\\/ \\/"),
        ("==", "="),
        ("=", "=="),
        ("[", "[ ["),
        ("]", "] ]"),
        ("{", "{ {"),
        ("}", "} }"),
    ]
    for old, new in patterns:
        pos = content.find(old)
        while pos != -1:
            mutated = content[:pos] + new + content[pos + len(old) :]
            mutations.append((f"{old}->{new}_at_{pos}", mutated))
            pos = content.find(old, pos + 1)

    # Add/remove a space after common keywords
    for kw in ["PROOF", "QED", "HAVE", "TAKE", "WITNESS", "ASSERT", "BY", "OBVIOUS", "OMITTED"]:
        pos = content.find(kw)
        while pos != -1:
            end = pos + len(kw)
            if end < len(content) and content[end] == " ":
                # Remove that space
                mutated = content[:end] + content[end + 1 :]
                mutations.append((f"remove_space_after_{kw}_at_{pos}", mutated))
            elif end < len(content) and content[end] != " ":
                # Insert space
                mutated = content[:end] + " " + content[end:]
                mutations.append((f"insert_space_after_{kw}_at_{pos}", mutated))
            pos = content.find(kw, end)

    # Insert/remove a newline after a module item
    for sep in [" Vera", " ", "\n"]:
        count = content.count(sep)
        if count > 0:
            pos = content.find(sep)
            mutated = insert_char(content, pos, "\n")
            mutations.append((f"insert_newline_at_{pos}", mutated))
            mutated = delete_char(content, pos)
            mutations.append((f"delete_char_at_{pos}", mutated))

    return mutations


def run_mutation_tests(original: str, max_mutations: int = 200):
    orig_diags, orig_msgs = parse_content(original)
    print(f"Original: {orig_diags} diagnostics")

    mutations = generate_mutations(original)
    random.shuffle(mutations)
    mutations = mutations[:max_mutations]

    results = {"killed": 0, "survived": 0, "same": 0}
    survivors = []
    for name, mutated in mutations:
        diags, msgs = parse_content(mutated)
        if orig_diags == 0 and diags == 0:
            results["same"] += 1
            survivors.append((name, diags, msgs))
        elif diags > 0:
            results["killed"] += 1
        else:
            results["survived"] += 1
            survivors.append((name, diags, msgs))

    print(
        f"Tested {len(mutations)} mutations: killed={results['killed']}, survived={results['survived']}, same={results['same']}"
    )

    if survivors:
        print("\nSurviving mutations (potential blind spots):")
        for name, diags, msgs in survivors[:10]:
            print(f"  {name}: {diags} diags")
            for m in msgs[:3]:
                print(f"    {m}")


def main():
    parser = argparse.ArgumentParser(description="Mutation testing for diagnostics")
    parser.add_argument("file", type=Path, help="TLA+ file to mutate")
    parser.add_argument(
        "--max-mutations",
        type=int,
        default=200,
        help="Maximum number of mutations to test (default: 200)",
    )
    args = parser.parse_args()

    original = args.file.read_text()
    random.seed(12345)
    run_mutation_tests(original, max_mutations=args.max_mutations)


if __name__ == "__main__":
    main()
