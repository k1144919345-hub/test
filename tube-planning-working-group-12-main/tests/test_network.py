import numpy as np
import pytest

from tube_planning._exceptions import TubePlanningError
from tube_planning.networks.network import Network
from tube_planning.flow import Flow


def simple_network():
    return Network(adj_mat=np.array([[0, 3], [3, 0]], dtype=float))


def test_bfs_and_path_reconstruction():
    net = simple_network()
    trace = net.bfs(0)
    path = net.path_from_bfs(trace, 1)
    assert path == [0, 1]


def test_bfs_unreachable_raises():
    net = Network(adj_mat=np.zeros((2, 2)))
    trace = net.bfs(0)
    with pytest.raises(TubePlanningError):
        net.path_from_bfs(trace, 1)


def test_capacity_constraint_exceed_raises():
    net = simple_network()
    flow = Flow.zero_flow(2, sources=(0,), sinks=(1,))
    flow.send_flow_along([0, 1], 4)
    with pytest.raises(TubePlanningError):
        net.capacity_constraint(flow)


def test_edmonds_karp_max_flow_value():
    net = simple_network()
    flow = net.edmonds_karp(0, 1, maxiter=10)
    assert pytest.approx(flow.value) == 3


def test_maximum_flow_disjoint_check():
    net = simple_network()
    with pytest.raises(TubePlanningError):
        net.maximum_flow([0], [0])


def test_sufficient_flow_success_and_failure():
    net = simple_network()
    ok_flow = net.sufficient_flow({0: 2}, {1: 2}, maxiter=10)
    assert pytest.approx(ok_flow.value) == 2
    with pytest.raises(TubePlanningError):
        net.sufficient_flow({0: 1}, {1: 2}, maxiter=10)
