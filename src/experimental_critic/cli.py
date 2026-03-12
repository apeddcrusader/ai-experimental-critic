"""Command-line interface for the experimental critique engine."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from experimental_critic.core import CriticEngine
from experimental_critic.utils import load_proposal, write_json

# ------------------------------------------------------------------
# Text formatter
# ------------------------------------------------------------------


def _format_text(report_dict: dict) -> str:
    """Return a human-readable text representation of the critique report."""
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("EXPERIMENT CRITIQUE REPORT")
    lines.append("=" * 72)
    lines.append(f"Proposal: {report_dict['proposal_summary']}")
    lines.append(
        f"Overall score: {report_dict['overall_score']:.2f}  "
        f"({report_dict['total_findings']} finding(s))"
    )
    lines.append("-" * 72)

    for i, f in enumerate(report_dict["findings"], 1):
        sev = f["severity"].upper()
        lines.append(f"  [{sev}] #{i} {f['rule_id']}")
        lines.append(f"    {f['message']}")
        lines.append(f"    -> {f['recommendation']}")
        lines.append("")

    if not report_dict["findings"]:
        lines.append("  No issues found. Well-designed proposal!")
        lines.append("")

    lines.append("=" * 72)
    return "\n".join(lines)


# ------------------------------------------------------------------
# Subcommand: critique
# ------------------------------------------------------------------


def _cmd_critique(args: argparse.Namespace) -> None:
    """Run critique on a proposal JSON file."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    proposal = load_proposal(input_path)
    engine = CriticEngine()
    report = engine.critique(proposal)
    report_dict = asdict(report)

    # Output
    if args.format == "json":
        output_text = json.dumps(report_dict, indent=2)
    else:
        output_text = _format_text(report_dict)

    if args.output:
        output_path = Path(args.output)
        if args.format == "json":
            write_json(report_dict, output_path)
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_text + "\n", encoding="utf-8")
        print(f"Report written to {output_path}")
    else:
        print(output_text)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = argparse.ArgumentParser(
        prog="ai-experimental-critic",
        description=(
            "Rule-based critique engine for experiment proposals "
            "identifying missing controls and biases"
        ),
    )
    parser.add_argument("--version", action="version", version="0.1.0")

    subparsers = parser.add_subparsers(dest="command")

    # critique subcommand
    crit = subparsers.add_parser(
        "critique",
        help="Critique an experiment proposal JSON file",
    )
    crit.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to a proposal JSON file",
    )
    crit.add_argument(
        "--format",
        "-f",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    crit.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write report to this path instead of stdout",
    )

    args = parser.parse_args(argv)

    if args.command == "critique":
        _cmd_critique(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
