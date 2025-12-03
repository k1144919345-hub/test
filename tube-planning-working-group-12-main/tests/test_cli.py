import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tube_planning.networks.proposal import Proposal


def write_matrix(path: Path, mat):
    np.savetxt(path, mat, delimiter=",", fmt="%.0f")


def test_cli_outputs_sorted_results(tmp_path):
    Proposal._all_proposals.clear()
    # current network 2 capacity
    net_file = tmp_path / "network.csv"
    write_matrix(net_file, np.array([[0, 2], [2, 0]], dtype=float))

    # proposals CSV: name,u,v,w
    proposals_file = tmp_path / "proposals.csv"
    proposals_file.write_text("better,0,1,4\nworse,0,1,1\n")

    # criteria: essential performance, desirable cost
    criteria_file = tmp_path / "crit.json"
    criteria = {
        "essential": [
            {
                "sources": [0],
                "sinks": [1],
                "supplies": None,
                "demands": None,
                "description": "perf",
                "weight": 1.0,
            }
        ],
        "desirable": [
            {"costs": ["total"], "budget": 10, "description": "cost", "weight": 1.0}
        ],
    }
    criteria_file.write_text(json.dumps(criteria))

    costs_file = tmp_path / "costs.json"
    costs_file.write_text(json.dumps({"new": 1, "ext": 1, "hire": 1, "train": 1}))

    cmd = [
        sys.executable,
        "-m",
        "tube_planning.evaluation",
        "-n",
        str(net_file),
        "-p",
        str(proposals_file),
        "-c",
        str(criteria_file),
        "-f",
        str(costs_file),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "name,score,failed_essentials"
    # With vehicle cost, lower-capacity proposal may rank higher
    assert lines[1].startswith("worse,")
