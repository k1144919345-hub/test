"""Evaluation helpers for scoring proposals."""

from __future__ import annotations

from typing import Iterable, Sequence
import numpy as np

from tube_planning.criteria.group import CriteriaGroup
from tube_planning.networks import Network, Proposal
from tube_planning.utils import CLIParser, read_fixed_costs
import csv
import json
from pathlib import Path


def evaluate_proposal(
    proposal: Proposal,
    current: Network,
    criteria: CriteriaGroup,
    costing_information: dict | None = None,
):
    """Evaluate a single proposal against the provided criteria.

    Returns
    -------
    tuple[float, list]
        Overall score and list of failed essential criteria.
    """
    return criteria.evaluate(proposal, current, costing_information)


def evaluate_proposals(
    proposals: Iterable[Proposal],
    current: Network,
    criteria: CriteriaGroup,
    costing_information: dict | None = None,
) -> list[tuple[Proposal, float, list]]:
    """Evaluate and rank a collection of proposals.

    Proposals with failed essential criteria are kept but will tend to score
    lower (negative contribution from failing criteria).
    """
    results: list[tuple[Proposal, float, list]] = []
    for p in proposals:
        score, failed = evaluate_proposal(p, current, criteria, costing_information)
        results.append((p, score, failed))
    results.sort(key=lambda t: t[1], reverse=True)
    return results


def _load_network(path: Path) -> Network:
    data = np.loadtxt(path, delimiter=",")
    # If 2D square treat as adjacency matrix
    if data.ndim == 2 and data.shape[0] == data.shape[1]:
        return Network(adj_mat=data)
    # Otherwise treat as edge list rows of length 3
    edges = []
    if data.ndim == 1:
        data = data.reshape(1, -1)
    for row in data:
        if len(row) < 2:
            continue
        u, v = int(row[0]), int(row[1])
        w = float(row[2]) if len(row) > 2 else 1.0
        edges.append((u, v, w))
    return Network(edge_table=edges)


def _load_proposals(path: Path) -> list[Proposal]:
    proposals: dict[str, list[tuple[int, int, float]]] = {}
    if path.suffix.lower() == ".json":
        with open(path, "r") as fh:
            raw = json.load(fh)
        # Allow either list of dicts or mapping name->edges
        if isinstance(raw, dict):
            iterable = raw.items()
        else:
            iterable = ((item["name"], item["edges"]) for item in raw)
        for name, edges in iterable:
            tbl = []
            for e in edges:
                if len(e) < 2:
                    continue
                u, v = int(e[0]), int(e[1])
                w = float(e[2]) if len(e) > 2 else 1.0
                tbl.append((u, v, w))
            proposals[name] = tbl
    else:
        with open(path, newline="") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if len(row) < 3:
                    continue
                name = row[0]
                try:
                    u, v = int(row[1]), int(row[2])
                    w = float(row[3]) if len(row) > 3 else 1.0
                except ValueError:
                    continue
                proposals.setdefault(name, []).append((u, v, w))

    return [Proposal(n, edge_table=tbl) for n, tbl in proposals.items()]


def main(argv: Sequence[str] | None = None) -> int:
    """Command line entry point for evaluating proposals."""
    parser = CLIParser(description="Evaluate tube proposals against criteria.")
    parser.add_argument(
        "-n",
        "--network",
        required=True,
        help="Path to current network file (CSV edge list or adjacency matrix).",
    )
    parser.add_argument(
        "-p",
        "--proposals",
        required=True,
        help="Path to proposals file (CSV with name,u,v,w or JSON).",
    )
    parser.add_argument(
        "-c",
        "--criteria",
        required=True,
        help="Path to criteria configuration file (.json/.cfile).",
    )
    parser.add_argument(
        "-f",
        "--costs",
        required=False,
        help="Optional path to costs file (JSON or CSV key,value).",
    )

    args = parser.parse_args(argv)

    network_path = Path(args.network)
    proposals_path = Path(args.proposals)
    criteria_path = Path(args.criteria)
    costs_path = Path(args.costs) if args.costs else None

    current_network = _load_network(network_path)
    proposals = _load_proposals(proposals_path)
    criteria = CriteriaGroup.from_file(criteria_path)
    costs = read_fixed_costs(costs_path) if costs_path else {}

    results = evaluate_proposals(proposals, current_network, criteria, costs)

    # Output as CSV for deterministic parsing
    print("name,score,failed_essentials")
    for proposal, score, failed in results:
        print(f"{proposal.name},{score:.6f},{len(failed)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
