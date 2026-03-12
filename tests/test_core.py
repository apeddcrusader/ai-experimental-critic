"""Tests for the critique engine core logic."""

from __future__ import annotations

from experimental_critic.core import CriticEngine
from experimental_critic.schemas import ExperimentProposal
from experimental_critic.utils import load_proposal
from tests.conftest import DEMO_DATA

# ---------------------------------------------------------------------------
# Fixtures (inline for clarity)
# ---------------------------------------------------------------------------


def _bad_proposal() -> ExperimentProposal:
    return load_proposal(DEMO_DATA / "proposal_1.json")


def _good_proposal() -> ExperimentProposal:
    return load_proposal(DEMO_DATA / "proposal_2.json")


def _mediocre_proposal() -> ExperimentProposal:
    return load_proposal(DEMO_DATA / "proposal_3.json")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_missing_negative_control_detected():
    """Bad proposal (empty controls) should trigger missing_negative_control."""
    engine = CriticEngine()
    report = engine.critique(_bad_proposal())
    rule_ids = [f.rule_id for f in report.findings]
    assert "missing_negative_control" in rule_ids


def test_no_blinding_detected():
    """Bad proposal (blinding=null) should trigger no_blinding."""
    engine = CriticEngine()
    report = engine.critique(_bad_proposal())
    rule_ids = [f.rule_id for f in report.findings]
    assert "no_blinding" in rule_ids


def test_underpowered_detected():
    """Bad proposal (sample_size=5) should trigger underpowered_sample."""
    engine = CriticEngine()
    report = engine.critique(_bad_proposal())
    rule_ids = [f.rule_id for f in report.findings]
    assert "underpowered_sample" in rule_ids


def test_good_proposal_few_findings():
    """Good proposal should have at most 2 findings."""
    engine = CriticEngine()
    report = engine.critique(_good_proposal())
    assert report.total_findings <= 2


def test_overall_score_range():
    """Overall score must be between 0.0 and 1.0 inclusive."""
    engine = CriticEngine()
    for loader in (_bad_proposal, _good_proposal, _mediocre_proposal):
        report = engine.critique(loader())
        assert 0.0 <= report.overall_score <= 1.0


def test_mediocre_has_some_findings():
    """Mediocre proposal should have at least 1 finding but fewer than 10."""
    engine = CriticEngine()
    report = engine.critique(_mediocre_proposal())
    assert 1 <= report.total_findings < 10


def test_all_rules_run():
    """Engine must have at least 10 registered rules."""
    engine = CriticEngine()
    assert len(engine.rules) >= 10


def test_bad_proposal_score_below_good():
    """Bad proposal must score strictly lower than the good proposal."""
    engine = CriticEngine()
    bad_report = engine.critique(_bad_proposal())
    good_report = engine.critique(_good_proposal())
    assert bad_report.overall_score < good_report.overall_score


def test_finding_severities_valid():
    """All findings must have a valid severity value."""
    engine = CriticEngine()
    report = engine.critique(_bad_proposal())
    valid = {"critical", "warning", "info"}
    for f in report.findings:
        assert f.severity in valid, f"Invalid severity: {f.severity}"


def test_report_total_matches_findings_length():
    """total_findings must equal len(findings)."""
    engine = CriticEngine()
    for loader in (_bad_proposal, _good_proposal, _mediocre_proposal):
        report = engine.critique(loader())
        assert report.total_findings == len(report.findings)
