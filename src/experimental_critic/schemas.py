"""Data schemas for experimental critique engine."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExperimentProposal:
    """A structured experiment proposal to be critiqued."""

    hypothesis: str
    methods: str
    controls: list[str] = field(default_factory=list)
    sample_size: int | None = None
    variables: list[str] = field(default_factory=list)
    blinding: str | None = None
    randomization: bool | None = None
    statistical_test: str | None = None
    replication: int | None = None


@dataclass
class Finding:
    """A single critique finding from a rule check."""

    rule_id: str
    severity: str  # "critical" | "warning" | "info"
    message: str
    recommendation: str


@dataclass
class CritiqueReport:
    """Full critique report for an experiment proposal."""

    proposal_summary: str
    findings: list[Finding] = field(default_factory=list)
    overall_score: float = 1.0
    total_findings: int = 0
