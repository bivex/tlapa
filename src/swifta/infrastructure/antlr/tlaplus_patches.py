"""Python 3.13+ compatibility patches for ANTLR-generated TLA+ parser."""

from __future__ import annotations


def patch() -> None:
    """Apply patches to generated parser to work with Python 3.13+."""
    # The generated parser uses Java-style listener patterns that don't match Python's
    # This is a placeholder for future patches if needed
    pass
