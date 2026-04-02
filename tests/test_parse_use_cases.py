"""Integration tests for TLA+ parsing use cases."""

from pathlib import Path

import pytest

from swifta.application.dto import ParseDirectoryCommand, ParseFileCommand
from swifta.application.use_cases import ParsingJobService
from swifta.infrastructure.antlr.parser_adapter import AntlrTlaplusSyntaxParser
from swifta.infrastructure.filesystem.source_repository import FileSystemSourceRepository
from swifta.infrastructure.system import (
    InMemoryParsingJobRepository,
    StructuredLoggingEventPublisher,
    SystemClock,
)

_FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def service() -> ParsingJobService:
    return ParsingJobService(
        source_repository=FileSystemSourceRepository(),
        parser=AntlrTlaplusSyntaxParser(),
        event_publisher=StructuredLoggingEventPublisher(),
        clock=SystemClock(),
        job_repository=InMemoryParsingJobRepository(),
    )


def test_parse_valid_tla_file(service: ParsingJobService) -> None:
    report = service.parse_file(ParseFileCommand(path=str(_FIXTURES / "valid.tla")))

    assert report.summary.source_count == 1
    assert report.summary.technical_failure_count == 0

    source = report.sources[0]
    assert source.status in ("succeeded", "succeeded_with_diagnostics")
    assert source.grammar_version.startswith("antlr4@4.13.1")

    kinds = {element.kind for element in source.structural_elements}
    assert "module" in kinds
    assert "variable" in kinds
    assert "operator_definition" in kinds


def test_parse_directory(service: ParsingJobService) -> None:
    report = service.parse_directory(ParseDirectoryCommand(root_path=str(_FIXTURES)))
    assert report.summary.source_count >= 1


def test_parse_extracts_module_name(service: ParsingJobService) -> None:
    report = service.parse_file(ParseFileCommand(path=str(_FIXTURES / "valid.tla")))
    source = report.sources[0]

    module_elements = [e for e in source.structural_elements if e.kind == "module"]
    assert len(module_elements) == 1
    assert module_elements[0].name == "TestFixture"


def test_parse_extracts_variables(service: ParsingJobService) -> None:
    report = service.parse_file(ParseFileCommand(path=str(_FIXTURES / "valid.tla")))
    source = report.sources[0]

    var_elements = [e for e in source.structural_elements if e.kind == "variable"]
    var_names = {e.name for e in var_elements}
    assert "x" in var_names
    assert "y" in var_names
