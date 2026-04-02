"""Nassi-Shneiderman diagram blocks for TLA+ operators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Block:
    """Base NSD block."""

    kind: str  # 'sequence', 'selection', 'case', 'action', 'iteration', 'scope'
    label: str = ""
    children: List[Block] = None
    condition: Optional[str] = None
    text: Optional[str] = None  # for action blocks

    def __post_init__(self) -> None:
        if self.children is None:
            self.children = []


@dataclass
class SequenceBlock(Block):
    """A sequence of blocks executed in order."""

    kind: str = "sequence"

    def __post_init__(self) -> None:
        super().__post_init__()
        self.label = ""


@dataclass
class SelectionBlock(Block):
    """IF-THEN-ELSE selection."""

    kind: str = "selection"
    then_branch: Block = None
    else_branch: Optional[Block] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.then_branch is None:
            self.then_branch = EmptyBlock()
        self.children = [self.then_branch] + ([self.else_branch] if self.else_branch else [])


@dataclass
class CaseBlock(Block):
    """CASE expression with multiple arms."""

    kind: str = "case"
    arms: List[tuple[str, Block]] = None  # (pattern, body)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.arms is None:
            self.arms = []
        self.children = [body for _, body in self.arms]


@dataclass
class ActionBlock(Block):
    """A single atomic action (assignment, predicate)."""

    kind: str = "action"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.text is None:
            self.text = self.label
        self.label = ""


@dataclass
class ScopeBlock(Block):
    """LET...IN or other scoped constructs."""

    kind: str = "scope"

    def __post_init__(self) -> None:
        super().__post_init__()


@dataclass
class EmptyBlock(Block):
    """Placeholder for empty else branch."""

    kind: str = "empty"

    def __post_init__(self) -> None:
        super().__post_init__()
        self.text = "skip"
