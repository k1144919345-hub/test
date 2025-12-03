import numpy as np
import pytest

from tube_planning._exceptions import TubePlanningError
from tube_planning.flow import Flow


def test_flow_creation_invalid_shape():
    with pytest.raises(TubePlanningError):
        Flow(np.zeros((2, 3)), sources=[], sinks=[])


def test_send_flow_skew_symmetric_and_value():
    f = Flow.zero_flow(2, sources=(0,), sinks=(1,))
    f.send_flow_along([0, 1], 5)
    assert f.flow_matrix[0, 1] == 5
    assert f.flow_matrix[1, 0] == -5
    # net flow at sink is 5, at source is -5
    assert pytest.approx(f.value) == 5


def test_non_conserving_flow_rejected():
    mat = np.array([[0, 1], [-1, 0]], dtype=float)
    # imbalance at node 0 if no terminals
    with pytest.raises(TubePlanningError):
        Flow(mat, sources=(), sinks=())
