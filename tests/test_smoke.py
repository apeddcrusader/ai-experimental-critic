"""Smoke tests for package import and end-to-end pipeline."""

from __future__ import annotations

from dataclasses import asdict

from tests.conftest import DEMO_DATA


def test_import():
    """Package should be importable and expose __version__."""
    import experimental_critic

    assert hasattr(experimental_critic, "__version__")


def test_full_critique_pipeline():
    """End-to-end: load JSON -> critique -> report dict."""
    from experimental_critic.core import CriticEngine
    from experimental_critic.utils import load_proposal

    proposal = load_proposal(DEMO_DATA / "proposal_1.json")
    engine = CriticEngine()
    report = engine.critique(proposal)
    report_dict = asdict(report)

    assert isinstance(report_dict, dict)
    assert "findings" in report_dict
    assert "overall_score" in report_dict
    assert report_dict["total_findings"] == len(report_dict["findings"])
    assert report_dict["total_findings"] > 0
