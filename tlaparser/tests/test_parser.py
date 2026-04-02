#!/usr/bin/env python3
"""
Test harness for the TLA+ Python parser.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tlaparser import parse_tla, parse_expression, get_tokens, TLAErrorListener


def test_tokenize():
    """Test basic tokenization."""
    print("=== Test: Tokenization ===")
    # BEGIN_MODULE is skipped (mode switch), so tokens in SPEC mode are:
    # IDENTIFIER, SEPARATOR, END_MODULE
    tokens = get_tokens("---- MODULE Test ----\n====")
    for tok in tokens:
        print(f"  {tok['type']:30s}  '{tok['text']}'")
    assert any(t["type"] == "IDENTIFIER" for t in tokens), "Should find IDENTIFIER token"
    assert any(t["type"] == "SEPARATOR" for t in tokens), "Should find SEPARATOR token"
    print("  PASSED\n")


def test_parse_simple_module():
    """Test parsing a minimal TLA+ module."""
    print("=== Test: Simple Module ===")
    source = """
---- MODULE Test ----
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully (no errors)")
    assert not errors, f"Expected no errors, got {errors}"
    print("  PASSED\n")


def test_parse_module_with_extends():
    """Test parsing a module with EXTENDS."""
    print("=== Test: Module with EXTENDS ===")
    source = """
---- MODULE NaturalsExt ----
EXTENDS Naturals, Integers
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_variable_declarations():
    """Test parsing variable declarations."""
    print("=== Test: Variable Declarations ===")
    source = """
---- MODULE VarTest ----
VARIABLE x, y, z
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_constant_declarations():
    """Test parsing CONSTANT declarations."""
    print("=== Test: Constant Declarations ===")
    source = """
---- MODULE ConstTest ----
CONSTANT N, Op(_,_)
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_simple_definition():
    """Test parsing operator definitions."""
    print("=== Test: Simple Definition ===")
    source = """
---- MODULE DefTest ----
x == 42
y == x + 1
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_function_definition():
    """Test parsing function definitions."""
    print("=== Test: Function Definition ===")
    source = """
---- MODULE FcnTest ----
f[x \\in Nat] == x * x
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_if_then_else():
    """Test parsing IF/THEN/ELSE."""
    print("=== Test: IF/THEN/ELSE ===")
    source = """
---- MODULE IfTest ----
max(a, b) == IF a > b THEN a ELSE b
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_let_in():
    """Test parsing LET/IN."""
    print("=== Test: LET/IN ===")
    source = """
---- MODULE LetTest ----
result == LET x == 1 y == 2 IN x + y
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_quantifier():
    """Test parsing quantifiers."""
    print("=== Test: Quantifiers ===")
    source = """
---- MODULE QuantTest ----
exists == \\E x \\in S : x > 0
forall == \\A x \\in Nat : x >= 0
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_set_constructor():
    """Test parsing set constructors."""
    print("=== Test: Set Constructors ===")
    source = """
---- MODULE SetTest ----
s1 == {1, 2, 3}
s2 == {x \\in Nat : x < 10}
s3 == {x + 1 : x \\in S}
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_conjunction_disjunction():
    """Test parsing bulleted conjunction/disjunction."""
    print("=== Test: Conjunction/Disjunction ===")
    source = """
---- MODULE ConjTest ----
spec == /\\ x > 0
       /\\ y < 10
       /\\ x + y > 5
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_theorem():
    """Test parsing THEOREM."""
    print("=== Test: Theorem ===")
    source = """
---- MODULE ThmTest ----
THEOREM 1 + 1 = 2
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_realistic_module():
    """Test parsing a more realistic TLA+ module."""
    print("=== Test: Realistic Module ===")
    source = """
---- MODULE Realistic ----
EXTENDS Naturals

VARIABLES x, y

Init == /\\ x = 0
        /\\ y = 0

Next == /\\ x' = x + 1
        /\\ y' = y + x

Spec == Init /\\ [][Next]_<<x, y>>

Inv == x >= 0 /\\ y >= 0

THEOREM Spec => []Inv
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_record_constructor():
    """Test parsing record constructors."""
    print("=== Test: Record Constructor ===")
    source = """
---- MODULE RcdTest ----
person == [name |-> "Alice", age |-> 30]
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_except():
    """Test parsing EXCEPT expressions."""
    print("=== Test: EXCEPT ===")
    source = """
---- MODULE ExceptTest ----
updated == [s EXCEPT ![1] = 42, !.name = "Bob"]
====
"""
    tree = parse_tla(source)
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed successfully")
    print("  PASSED\n")


def test_parse_expression_simple():
    """Test parsing standalone expressions."""
    print("=== Test: Standalone Expression ===")
    tree = parse_expression("1 + 2 * 3")
    errors = tree._errors
    if errors:
        for e in errors:
            print(f"  ERROR line {e['line']}:{e['column']} - {e['message']}")
    else:
        print("  Parsed '1 + 2 * 3' successfully")
    print("  PASSED\n")


if __name__ == "__main__":
    tests = [
        test_tokenize,
        test_parse_simple_module,
        test_parse_module_with_extends,
        test_parse_variable_declarations,
        test_parse_constant_declarations,
        test_parse_simple_definition,
        test_parse_function_definition,
        test_parse_if_then_else,
        test_parse_let_in,
        test_parse_quantifier,
        test_parse_set_constructor,
        test_parse_conjunction_disjunction,
        test_parse_theorem,
        test_parse_realistic_module,
        test_parse_record_constructor,
        test_parse_except,
        test_parse_expression_simple,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}\n")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'=' * 50}")
