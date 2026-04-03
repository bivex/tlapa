"""Tests for grammar features: temporal ops, proofs, LAMBDA, CHOOSE, cache, error reporting."""

from pathlib import Path

import pytest

from swifta.application.dto import ParseFileCommand
from swifta.application.use_cases import ParsingJobService
from swifta.domain.model import DiagnosticSeverity, SourceUnit, SourceUnitId, SyntaxDiagnostic
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
    def test_use_hide_and_proof_steps(self, service: ParsingJobService) -> None:
        report = _parse_fixture(service, "use_hide.tla")
        source = report.sources[0]
        assert source.status in ("succeeded", "succeeded_with_diagnostics")
        kinds = {element.kind for element in source.structural_elements}
        assert "theorem" in kinds
        assert "operator_definition" in kinds
        # USE and HIDE are extracted as top-level kinds
        assert "use" in kinds
        assert "hide" in kinds
        # Proof steps (TAKE, WITNESS, HAVE) are extracted under 'proof' kind
        proof_elems = [e for e in source.structural_elements if e.kind == "proof"]
        proof_names = {e.name for e in proof_elems}
        assert any("TAKE" in n for n in proof_names)
        assert any("WITNESS" in n for n in proof_names)
        assert any("HAVE" in n for n in proof_names)
        take_sigs = [e.signature for e in proof_elems if "TAKE" in e.name]
        witness_sigs = [e.signature for e in proof_elems if "WITNESS" in e.name]
        assert any("TAKEn\\inNat" in sig for sig in take_sigs if sig)
        assert any("WITNESS n+1" in sig for sig in witness_sigs if sig)
        assert any("OBVIOUS" in n for n in proof_names)
        assert any("QED" in n for n in proof_names)


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
        assert outcome.status == "succeeded_with_diagnostics"
        assert len(outcome.diagnostics) > 0

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

    def test_error_recovery_collects_diagnostics(self) -> None:
        content = "---- MODULE Err ----\nVARIABLE x\nInit == x = 0\nNext == x' = 1\n===="
        source_unit = SourceUnit(
            identifier=SourceUnitId("err"),
            location="err.tla",
            content=content,
        )
        parser = AntlrTlaplusSyntaxParser()
        outcome = parser.parse(source_unit)
        assert outcome.status in ("succeeded", "succeeded_with_diagnostics")

    def test_missing_module_begin_marker(self) -> None:
        content = "VARIABLE x\nInit == x = 0\n===="
        source_unit = SourceUnit(
            identifier=SourceUnitId("nobegin"),
            location="nobegin.tla",
            content=content,
        )
        parser = AntlrTlaplusSyntaxParser()
        outcome = parser.parse(source_unit)
        assert len(outcome.diagnostics) > 0

    def test_hint_for_missing_end_marker(self) -> None:
        content = "---- MODULE NoEnd ----\nVARIABLE x\nInit == x = 0"
        source_unit = SourceUnit(
            identifier=SourceUnitId("noend"),
            location="noend.tla",
            content=content,
        )
        parser = AntlrTlaplusSyntaxParser()
        outcome = parser.parse(source_unit)
        msgs = " ".join(d.message for d in outcome.diagnostics)
        assert "====" in msgs or "close the module" in msgs or len(outcome.diagnostics) > 0

    def test_diagnostic_has_end_location(self) -> None:
        from swifta.infrastructure.antlr.error_listener import CollectingErrorListener

        listener = CollectingErrorListener()
        mock_token = type("Token", (), {"text": "====", "line": 1, "column": 0})()
        listener.syntaxError(None, mock_token, 1, 0, "missing '===='", None)
        assert len(listener.diagnostics) == 1
        diag = listener.diagnostics[0]
        assert diag.line == 1
        assert diag.column == 0

    def test_format_diagnostic_with_source_context(self) -> None:
        from swifta.infrastructure.antlr.error_listener import format_diagnostic

        diag = SyntaxDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            message="missing '}'",
            line=2,
            column=5,
            end_line=2,
            end_column=6,
        )
        source_lines = ["---- MODULE Test ----", "S == {1, 2, 3", "===="]
        result = format_diagnostic(diag, source_lines)
        assert "ERROR" in result
        assert "L2:5" in result
        assert "S == {1, 2, 3" in result
        assert "^" in result

    def test_format_diagnostic_multi_line_range(self) -> None:
        from swifta.infrastructure.antlr.error_listener import format_diagnostic

        diag = SyntaxDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            message="multi-line error",
            line=2,
            column=0,
            end_line=4,
            end_column=10,
        )
        result = format_diagnostic(diag, None)
        assert "L2:0-L4:10" in result

    def test_classify_diagnostics_downgrades_false_positives(self) -> None:
        from swifta.infrastructure.antlr.parser_adapter import _classify_diagnostics

        diag = SyntaxDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            message="no viable alternative at input 'x+1'",
            line=3,
            column=5,
        )
        result = _classify_diagnostics((diag,), "---- MODULE T ----\nA == x+1\n====")
        assert len(result) == 1
        assert result[0].severity == DiagnosticSeverity.WARNING

    def test_classify_diagnostics_keeps_true_errors(self) -> None:
        from swifta.infrastructure.antlr.parser_adapter import _classify_diagnostics

        diag = SyntaxDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            message="missing '====' to close the module",
            line=5,
            column=0,
        )
        result = _classify_diagnostics((diag,), "---- MODULE T ----\nA == 1\n====")
        assert len(result) == 1
        assert result[0].severity == DiagnosticSeverity.ERROR


class TestWarningDiagnostics:
    def test_warning_collecting_listener(self) -> None:
        from swifta.infrastructure.antlr.error_listener import WarningCollectingListener

        listener = WarningCollectingListener()
        mock_token = type("Token", (), {"text": "bad", "line": 1, "column": 0})()
        listener.syntaxError(None, mock_token, 1, 0, "some warning", None)
        assert len(listener.diagnostics) == 1
        assert listener.diagnostics[0].severity == DiagnosticSeverity.WARNING

    def test_format_diagnostics_report(self) -> None:
        parser = AntlrTlaplusSyntaxParser()
        content = "---- MODULE Rep ----\nVARIABLE x\n===="
        source_unit = SourceUnit(
            identifier=SourceUnitId("rep"),
            location="rep.tla",
            content=content,
        )
        outcome = parser.parse(source_unit)
        report = parser.format_diagnostics_report(outcome.diagnostics)
        if outcome.diagnostics:
            assert isinstance(report, str)


class TestDiagnosticDTO:
    def test_dto_includes_end_location(self) -> None:
        from swifta.application.dto import SyntaxDiagnosticDTO

        dto = SyntaxDiagnosticDTO(
            severity="error",
            message="test",
            line=1,
            column=0,
            end_line=1,
            end_column=5,
        )
        d = dto.to_dict()
        assert d["end_line"] == 1
        assert d["end_column"] == 5

    def test_dto_defaults_end_location(self) -> None:
        from swifta.application.dto import SyntaxDiagnosticDTO

        dto = SyntaxDiagnosticDTO(
            severity="error",
            message="test",
            line=1,
            column=0,
        )
        d = dto.to_dict()
        assert d["end_line"] == 0
        assert d["end_column"] == 0
