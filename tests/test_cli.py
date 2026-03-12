"""Tests for the CLI interface."""

from __future__ import annotations

import json
import subprocess
import sys

from tests.conftest import DEMO_DATA


def test_cli_help():
    """CLI --help must exit 0 and mention the program name."""
    result = subprocess.run(
        [sys.executable, "-m", "experimental_critic", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "experimental-critic" in result.stdout.lower() or (
        "experimental_critic" in result.stdout.lower()
    )


def test_cli_critique_demo():
    """CLI critique subcommand runs on demo proposal_1 and prints text."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "experimental_critic",
            "critique",
            "--input",
            str(DEMO_DATA / "proposal_1.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "CRITIQUE REPORT" in result.stdout


def test_cli_critique_json_format():
    """CLI critique --format json produces valid JSON output."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "experimental_critic",
            "critique",
            "--input",
            str(DEMO_DATA / "proposal_2.json"),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "overall_score" in data
    assert "findings" in data


def test_cli_critique_output_file(tmp_path):
    """CLI critique --output writes a file."""
    out = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "experimental_critic",
            "critique",
            "--input",
            str(DEMO_DATA / "proposal_1.json"),
            "--format",
            "json",
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_findings"] > 0
