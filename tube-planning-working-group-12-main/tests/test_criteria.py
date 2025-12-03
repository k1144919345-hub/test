import json
from pathlib import Path

import numpy as np
import pytest

from tube_planning._exceptions import TubePlanningError
from tube_planning.criteria.cost import CostCriteria
from tube_planning.criteria.group import CriteriaFactory, CriteriaGroup
from tube_planning.criteria.performance import PerformanceCriteria
from tube_planning.evaluation import evaluate_proposals
from tube_planning.networks.network import Network
from tube_planning.networks.proposal import Proposal


def test_cost_criteria_budget_gap():
    crit = CostCriteria(costs="total", budget=10, description="", weight=1.0)
    costs = {"new": 1, "ext": 1, "hire": 1, "train": 1}
    assert crit.evaluate(Network(adj_mat=np.zeros((1, 1))), Network(adj_mat=np.zeros((1, 1))), costs) == 10
    with pytest.raises(TubePlanningError):
        crit.evaluate(None, None, {"infra": 1})


def test_performance_criteria_max_flow_diff():
    current = Network(adj_mat=np.array([[0, 2], [2, 0]], dtype=float))
    proposed = Network(adj_mat=np.array([[0, 4], [4, 0]], dtype=float))
    crit = PerformanceCriteria([0], [1], None, None, description="", weight=1.0)
    # combined has capacity 6 vs current 2, so improvement 4
    assert pytest.approx(crit.evaluate(proposed, current, {})) == 4


def test_performance_criteria_sufficient_flow_failure():
    net = Network(adj_mat=np.array([[0, 1], [1, 0]], dtype=float))
    crit = PerformanceCriteria([0], [1], [0.5], [1.0], description="", weight=1.0)
    assert crit.evaluate(net, net, {}) < 0  # insufficient supply triggers negative


def test_criteria_group_evaluate_and_file(tmp_path):
    essential = [
        PerformanceCriteria([0], [1], None, None, description="perf", weight=1.0)
    ]
    desirable = [CostCriteria(["total"], 5, description="cost", weight=1.0)]
    group = CriteriaGroup(essential=essential, desirable=desirable)

    path = tmp_path / "crit.cfile"
    group.to_criteria_file(path)
    loaded = CriteriaGroup.from_file(path)

    current = Network(adj_mat=np.array([[0, 1], [1, 0]], dtype=float))
    proposed = Network(adj_mat=np.array([[0, 2], [2, 0]], dtype=float))
    fixed = {"new": 1, "ext": 1, "hire": 0, "train": 0}
    score, failed = loaded.evaluate(proposed, current, fixed)
    assert failed == []
    assert score > 0


def test_evaluate_proposals_orders_by_score(tmp_path):
    Proposal._all_proposals.clear()
    current = Network(adj_mat=np.array([[0, 2], [2, 0]], dtype=float))
    better = Proposal("better", adj_mat=np.array([[0, 4], [4, 0]], dtype=float))
    worse = Proposal("worse", adj_mat=np.array([[0, 1], [1, 0]], dtype=float))

    crit = PerformanceCriteria([0], [1], None, None, description="", weight=1.0)
    group = CriteriaGroup(essential=[crit])

    results = evaluate_proposals([worse, better], current, group, {})
    assert results[0][0].name == "better"
