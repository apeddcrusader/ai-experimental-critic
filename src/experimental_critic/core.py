"""Core critique engine with rule-based checks for experiment proposals."""

from __future__ import annotations

from dataclasses import dataclass, field

from experimental_critic.schemas import CritiqueReport, ExperimentProposal, Finding

# ---------------------------------------------------------------------------
# Severity weights for overall score calculation
# ---------------------------------------------------------------------------
SEVERITY_WEIGHTS: dict[str, float] = {
    "critical": 0.10,
    "warning": 0.05,
    "info": 0.02,
}

# ---------------------------------------------------------------------------
# Keyword sets used by rules
# ---------------------------------------------------------------------------
NEGATIVE_CONTROL_KEYWORDS = {"negative", "vehicle", "untreated", "placebo", "sham"}
POSITIVE_CONTROL_KEYWORDS = {"positive", "known", "reference", "standard"}
MEASUREMENT_OBJECTIVITY_KEYWORDS = {"blinded", "automated", "quantitative", "objective"}
ENDPOINT_KEYWORDS = {"endpoint", "outcome", "measure", "primary"}

MIN_SAMPLE_SIZE = 10
MIN_REPLICATION = 3
MIN_VARIABLES = 2


def _text_contains_any(text: str, keywords: set[str]) -> bool:
    """Check whether *text* contains any of the *keywords* (case-insensitive)."""
    lower = text.lower()
    return any(kw in lower for kw in keywords)


def _controls_contain_any(controls: list[str], keywords: set[str]) -> bool:
    """Check whether any control string contains a keyword."""
    joined = " ".join(controls).lower()
    return any(kw in joined for kw in keywords)


# ---------------------------------------------------------------------------
# Individual rule functions
# ---------------------------------------------------------------------------


def _rule_missing_negative_control(p: ExperimentProposal) -> Finding | None:
    if not p.controls or not _controls_contain_any(p.controls, NEGATIVE_CONTROL_KEYWORDS):
        return Finding(
            rule_id="missing_negative_control",
            severity="critical",
            message="No negative / vehicle / untreated control identified.",
            recommendation=(
                "Add a negative control group (e.g. vehicle-only, untreated, "
                "or placebo) to establish a baseline."
            ),
        )
    return None


def _rule_missing_positive_control(p: ExperimentProposal) -> Finding | None:
    if not p.controls or not _controls_contain_any(p.controls, POSITIVE_CONTROL_KEYWORDS):
        return Finding(
            rule_id="missing_positive_control",
            severity="warning",
            message="No positive / known-effect control identified.",
            recommendation=(
                "Include a positive control with a known effect to validate assay sensitivity."
            ),
        )
    return None


def _rule_no_randomization(p: ExperimentProposal) -> Finding | None:
    if p.randomization is None or p.randomization is False:
        return Finding(
            rule_id="no_randomization",
            severity="critical",
            message="Randomization is absent or not specified.",
            recommendation=(
                "Randomize subject allocation to treatment groups to reduce selection bias."
            ),
        )
    return None


def _rule_no_blinding(p: ExperimentProposal) -> Finding | None:
    if not p.blinding:
        return Finding(
            rule_id="no_blinding",
            severity="critical",
            message="No blinding strategy specified.",
            recommendation=(
                "Implement at least single-blind (preferably double-blind) "
                "to reduce observer and performance bias."
            ),
        )
    return None


def _rule_underpowered_sample(p: ExperimentProposal) -> Finding | None:
    if p.sample_size is None or p.sample_size < MIN_SAMPLE_SIZE:
        return Finding(
            rule_id="underpowered_sample",
            severity="critical",
            message=(
                f"Sample size ({p.sample_size}) is below the recommended "
                f"minimum of {MIN_SAMPLE_SIZE}."
            ),
            recommendation=(
                "Perform a power analysis and increase sample size to ensure "
                "adequate statistical power (typically >=80%)."
            ),
        )
    return None


def _rule_no_replication(p: ExperimentProposal) -> Finding | None:
    if p.replication is None or p.replication < MIN_REPLICATION:
        return Finding(
            rule_id="no_replication",
            severity="warning",
            message=(
                f"Replication count ({p.replication}) is below the recommended "
                f"minimum of {MIN_REPLICATION}."
            ),
            recommendation=(
                "Replicate the experiment at least 3 independent times to confirm reproducibility."
            ),
        )
    return None


def _rule_no_statistical_test(p: ExperimentProposal) -> Finding | None:
    if not p.statistical_test:
        return Finding(
            rule_id="no_statistical_test",
            severity="critical",
            message="No statistical test specified.",
            recommendation=(
                "Pre-specify an appropriate statistical test (e.g. t-test, "
                "ANOVA, Mann-Whitney U) matched to data distribution and "
                "study design."
            ),
        )
    return None


def _rule_measurement_bias_risk(p: ExperimentProposal) -> Finding | None:
    if not _text_contains_any(p.methods, MEASUREMENT_OBJECTIVITY_KEYWORDS):
        return Finding(
            rule_id="measurement_bias_risk",
            severity="warning",
            message=(
                "Methods description lacks mention of blinded or automated "
                "measurement, raising measurement bias risk."
            ),
            recommendation=(
                "Use blinded assessment, automated scoring, or otherwise "
                "objective measurement methods to reduce measurement bias."
            ),
        )
    return None


def _rule_confounding_variables(p: ExperimentProposal) -> Finding | None:
    if len(p.variables) < MIN_VARIABLES:
        return Finding(
            rule_id="confounding_variables",
            severity="warning",
            message=(
                f"Only {len(p.variables)} variable(s) listed; potential "
                "confounders may be unaccounted for."
            ),
            recommendation=(
                "Identify and list all independent, dependent, and potential "
                "confounding variables. Consider controlling or measuring at "
                "least 2 key variables."
            ),
        )
    return None


def _rule_no_endpoint_defined(p: ExperimentProposal) -> Finding | None:
    if not _text_contains_any(p.methods, ENDPOINT_KEYWORDS):
        return Finding(
            rule_id="no_endpoint_defined",
            severity="warning",
            message="No clear endpoint or outcome measure found in methods.",
            recommendation=(
                "Define a primary endpoint / outcome measure explicitly in the methods section."
            ),
        )
    return None


# ---------------------------------------------------------------------------
# Rule type alias
# ---------------------------------------------------------------------------
RuleFunc = type(_rule_missing_negative_control)  # callable signature hint

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

_DEFAULT_RULES: list[RuleFunc] = [
    _rule_missing_negative_control,
    _rule_missing_positive_control,
    _rule_no_randomization,
    _rule_no_blinding,
    _rule_underpowered_sample,
    _rule_no_replication,
    _rule_no_statistical_test,
    _rule_measurement_bias_risk,
    _rule_confounding_variables,
    _rule_no_endpoint_defined,
]


@dataclass
class CriticEngine:
    """Rule-based critique engine for experiment proposals.

    Runs a collection of rule functions against an ``ExperimentProposal``
    and produces a ``CritiqueReport`` with findings and an overall score.
    """

    rules: list[RuleFunc] = field(default_factory=lambda: list(_DEFAULT_RULES))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def critique(self, proposal: ExperimentProposal) -> CritiqueReport:
        """Run all rules and return a critique report."""
        findings: list[Finding] = []
        for rule in self.rules:
            result = rule(proposal)
            if result is not None:
                findings.append(result)

        score = self._compute_score(findings)
        summary = self._summarize(proposal)

        return CritiqueReport(
            proposal_summary=summary,
            findings=findings,
            overall_score=score,
            total_findings=len(findings),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_score(findings: list[Finding]) -> float:
        """Compute overall score: 1.0 minus weighted penalties, clamped to 0."""
        penalty = sum(SEVERITY_WEIGHTS.get(f.severity, 0.0) for f in findings)
        return max(0.0, round(1.0 - penalty, 2))

    @staticmethod
    def _summarize(proposal: ExperimentProposal) -> str:
        """Create a one-line summary from the proposal hypothesis."""
        hyp = proposal.hypothesis.strip()
        if len(hyp) > 120:
            hyp = hyp[:117] + "..."
        return hyp
