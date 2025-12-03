from collections.abc import Iterable

import numpy as np

from tube_planning._exceptions import TubePlanningError


class Flow:
    """Represents a skew–symmetric flow on an undirected network."""

    _EPS = 1e-9

    @property
    def flow_in(self) -> np.ndarray:
        """Total incoming flow for each node (column sums)."""
        return self.flow_matrix.sum(axis=0)

    @property
    def flow_out(self) -> np.ndarray:
        """Total outgoing flow for each node (row sums)."""
        return self.flow_matrix.sum(axis=1)

    @property
    def net_flow(self) -> np.ndarray:
        """Net flow for each node (in minus out)."""
        return self.flow_in - self.flow_out

    @property
    def value(self) -> float:
        """Total flow delivered to sinks (or sent from sources if no sinks given)."""
        if self.sources:
            return float(np.sum(self.flow_out[list(self.sources)]))
        if self.sinks:
            return float(np.sum(self.flow_in[list(self.sinks)]))
        return 0.0

    @classmethod
    def zero_flow(
        cls, n_nodes: int, sources: Iterable[int] = (), sinks: Iterable[int] = ()
    ):
        """Creates the zero flow of a given size, with the corresponding sources and sinks.

        The zero flow can be created by calling this classmethod.

        Create the zero flow for a network of 6 nodes, with no sources or sinks:

        >>> from tube_planning.flow import Flow
        >>> zero_flow = Flow.zero_flow(6)

        Create the zero flow for a network of 6 nodes, flagging nodes 0 and 4 as the sources
        and node 3 as the sink:

        >>> from tube_planning.flow import Flow
        >>> zero_flow = Flow.zero_flow(6, sources=(0, 4), sinks=(3,))

        Args:
            n_nodes : int
                The size of the flow matrix, or equivalently the number of nodes in the
                network that this `Flow` will be used in conjunction with.
            sources : Iterable[int], default = ()
                Indexes of source nodes.
            sinks : Iterable[int], default = ()
                Indexes of sink nodes.

        Returns:
            f : Flow
                Zero flow of the requested size, with appropriate sources and sinks.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        return cls(np.zeros((n_nodes, n_nodes), dtype=float), sources, sinks)

    def __init__(self, flow_matrix, sources, sinks):
        matrix = np.asarray(flow_matrix, dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise TubePlanningError("Flow matrix must be square.")

        n = matrix.shape[0]
        self.flow_matrix = matrix
        self.sources = tuple(dict.fromkeys(int(s) for s in sources))
        self.sinks = tuple(dict.fromkeys(int(s) for s in sinks))

        for node in (*self.sources, *self.sinks):
            if node < 0 or node >= n:
                raise TubePlanningError("Source or sink index out of bounds.")

        if not self._conserves_flow():
            raise TubePlanningError("Flow does not conserve at intermediate nodes.")

    def _conserves_flow(self) -> bool:
        """Check skew-symmetry and flow conservation at non-terminal nodes."""
        if not np.allclose(self.flow_matrix, -self.flow_matrix.T, atol=self._EPS):
            return False
        if not np.allclose(np.diag(self.flow_matrix), 0.0, atol=self._EPS):
            return False

        net = self.net_flow
        terminals = set(self.sources) | set(self.sinks)
        for idx, value in enumerate(net):
            if idx in terminals:
                continue
            if not np.isclose(value, 0.0, atol=self._EPS):
                return False
        return True

    def send_flow_along(self, path, amount):
        """Send ``amount`` of flow along ``path``, updating the flow matrix."""
        if len(path) < 2:
            raise TubePlanningError("Path must contain at least two nodes.")

        for u, v in zip(path[:-1], path[1:], strict=True):
            if (
                u < 0
                or v < 0
                or u >= self.flow_matrix.shape[0]
                or v >= self.flow_matrix.shape[0]
            ):
                raise TubePlanningError("Path contains invalid node index.")
            self.flow_matrix[u, v] += amount
            self.flow_matrix[v, u] -= amount
