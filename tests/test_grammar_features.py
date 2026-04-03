"""Tests for grammar features: temporal ops, proofs, LAMBDA, CHOOSE, cache, error reporting."""

from pathlib import Path

import pytest

from swifta.application.dto import ParseFileCommand
from swifta.application.use_cases import ParsingJobService
from swifta.domain.model import SourceUnit, SourceUnitId
from swifta.infrastructure.antlr.parser_adapter import AntlrTlaplusSyntaxParser
from swifta.infrastructure.antlr.runtime import ParseCache, ParseTreeResult, get_global_cache
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


def _parse_fixture(service: ParsingJobService, name: str):
    return service.parse_file(ParseFileCommand(path=str(_FIXTURES / name)))


def _make_result(label: str = "tree") -> ParseTreeResult:
    return ParseTreeResult(token_stream=None, parser=None, tree=label, diagnostics=())


class TestTemporalOperators:
    def test_temporal_operators_parse(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "temporal.tla")
        source = report.sources[0]
        assert source.status in ("succeeded", "succeeded_with_diagnostics")
        kinds = {element.kind for element in source.structural_elements}
        assert "module" in kinds
        assert "operator_definition" in kinds
        names = {element.name for element in source.structural_elements}
        assert "AlwaysSafe" in names
        assert "EventuallyTrue" in names

    def test_wf_sf_fairness(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "temporal.tla")
        source = report.sources[0]
        assert source.status in ("succeeded", "succeeded_with_diagnostics")
        names = {element.name for element in source.structural_elements}
        assert "WF_Fair" in names
        assert "SF_Fair" in names

    def test_temporal_signatures(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "temporal.tla")
        source = report.sources[0]
        sigs = {
            element.name: element.signature
            for element in source.structural_elements
            if element.signature
        }
        assert "AlwaysSafe" in sigs
        assert "EventuallyTrue" in sigs


class TestProofSyntax:
    def test_proof_obvious(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "proof.tla")
        source = report.sources[0]
        assert source.status in ("succeeded", "succeeded_with_diagnostics")
        names = {element.name for element in source.structural_elements}
        assert "Thm1" in names
        assert "Thm2" in names

    def test_proof_steps(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "proof.tla")
        source = report.sources[0]
        assert source.status in ("succeeded", "succeeded_with_diagnostics")
        kinds = [element.kind for element in source.structural_elements]
        proof_count = kinds.count("proof")
        assert proof_count >= 1

    def test_theorem_with_proof(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "proof.tla")
        source = report.sources[0]
        names = {element.name for element in source.structural_elements}
        assert "AddComm" in names


class TestLambdaChoose:
    def test_lambda_expression(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "lambda_choose.tla")
        source = report.sources[0]
        assert source.status in ("succeeded", "succeeded_with_diagnostics")
        names = {element.name for element in source.structural_elements}
        assert "UseLambda" in names
        assert "ApplyLambda" in names

    def test_choose_expression(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "lambda_choose.tla")
        source = report.sources[0]
        names = {element.name for element in source.structural_elements}
        assert "ChooseMin" in names

    def test_choose_bound(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "lambda_choose.tla")
        source = report.sources[0]
        names = {element.name for element in source.structural_elements}
        assert "ChooseBound" in names


class TestUseHide:
    def test_use_in_proof(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "use_hide.tla")
        source = report.sources[0]
        assert source.status in ("succeeded", "succeeded_with_diagnostics")
        kinds = {element.kind for element in source.structural_elements}
        assert "theorem" in kinds
        assert "operator_definition" in kinds


class TestParseCache:
    def test_cache_stores_and_retrieves(self) -> None:
        cache = ParseCache(maxsize=4)
        r = _make_result("test_tree")
        cache.put("hello", "unit", r)
        assert cache.get("hello", "unit") is r

    def test_cache_evicts_lru(self) -> None:
        cache = ParseCache(maxsize=2)
        r1, r2, r3 = _make_result("r1"), _make_result("r2"), _make_result("r3")
        cache.put("a", "unit", r1)
        cache.put("b", "unit", r2)
        assert cache.size == 2
        cache.put("c", "unit", r3)
        assert cache.get("a", "unit") is None
        assert cache.get("b", "unit") is r2
        assert cache.get("c", "unit") is r3

    def test_cache_invalidate(self) -> None:
        cache = ParseCache(maxsize=4)
        r = _make_result("result")
        cache.put("x", "unit", r)
        assert cache.get("x", "unit") is r
        cache.invalidate("x", "unit")
        assert cache.get("x", "unit") is None

    def test_global_cache_is_shared(self) -> None:
        c1 = get_global_cache()
        c2 = get_global_cache()
        assert c1 is c2

    def test_cache_same_content_different_rule(self) -> None:
        cache = ParseCache(maxsize=4)
        r1, r2 = _make_result("r1"), _make_result("r2")
        cache.put("text", "unit", r1)
        cache.put("text", "expression", r2)
        assert cache.get("text", "unit") is r1
        assert cache.get("text", "expression") is r2

    def test_cache_clear(self) -> None:
        cache = ParseCache(maxsize=4)
        cache.put("a", "unit", _make_result("r1"))
        cache.put("b", "unit", _make_result("r2"))
        cache.clear()
        assert cache.size == 0
        assert cache.get("a", "unit") is None


class TestErrorReporting:
    def test_parse_missing_module_end(self, service: ParsingJobService) -> None:
        content = "---- MODULE Bad\nVARIABLE x\nInit == x = 0"
        source_unit = SourceUnit(
            identifier=SourceUnitId("bad"),
            location="bad.tla",
            content=content,
        )
        parser = AntlrTlaplusSyntaxParser()
        outcome = parser.parse(source_unit)
        assert outcome.source_unit_id.value == "bad"

    def test_parse_invalid_operator(self, service: ParsingJobService) -> None:
        content = "---- MODULE Bad2 ----\nEXTENDS Naturals\nFoo == ====\n===="
        source_unit = SourceUnit(
            identifier=SourceUnitId("bad2"),
            location="bad2.tla",
            content=content,
        )
        parser = AntlrTlaplusSyntaxParser()
        outcome = parser.parse(source_unit)
        assert outcome.source_unit_id.value == "bad2"

    def test_parse_existing_fixtures_succeed(self, service: ParsingJobService) -> None:
        for fixture_name in ("valid.tla", "allocator.tla"):
            report = _parse_fixture(service, fixture_name)
            source = report.sources[0]
            assert source.status in ("succeeded", "succeeded_with_diagnostics")
            kinds = {element.kind for element in source.structural_elements}
            assert "module" in kinds
