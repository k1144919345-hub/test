import numpy as np
import pytest

from tube_planning._exceptions import TubePlanningError
from tube_planning.networks.network import Network


def test_bfs_reaches_all_connected_nodes():
    adj = np.array(
        [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0],
        ],
        dtype=float,
    )
    net = Network(adj_mat=adj)
    trace = net.bfs(0)
    assert all(t >= 0 for t in trace)


def test_bfs_out_of_bounds_root_raises():
    net = Network(adj_mat=np.zeros((1, 1)))
    with pytest.raises(TubePlanningError):
        net.bfs(2)
