"""Utility functions for loading proposals and writing output."""

from __future__ import annotations

import json
from pathlib import Path

from experimental_critic.schemas import ExperimentProposal


def load_proposal(path: Path) -> ExperimentProposal:
    """Load an ``ExperimentProposal`` from a JSON file.

    The JSON keys must match the ``ExperimentProposal`` field names.
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return ExperimentProposal(**data)


def write_json(data: dict, path: Path) -> None:
    """Write *data* as pretty-printed JSON to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
