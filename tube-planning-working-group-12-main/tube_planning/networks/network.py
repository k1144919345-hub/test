import numpy as np

from tube_planning._exceptions import TubePlanningError
from tube_planning.flow import Flow


class Network:

    @property
    def n_nodes(self) -> int:
        return self.adjacency_matrix.shape[0]

    @staticmethod
    def path_from_bfs(path_trace, dest):
        if dest < 0 or dest >= len(path_trace):
            raise TubePlanningError("Destination node out of bounds.")
        if path_trace[dest] < 0:
            raise TubePlanningError("Destination is unreachable from root.")

        path = [dest]
        cur = dest
        while path_trace[cur] != cur:
            cur = path_trace[cur]
            path.append(cur)
        path.reverse()
        return path

    def __add__(self, other: "Network") -> "Network":
        """Combine two ``Network``s into one.

        ``Network``s are combined by element-wise addition of their adjacency matrix.
        This results in:

        - Any edge that is in exactly one of the two ``Networks``s is preserved in the resulting ``Network``.
        - Any edge that appears in both ``Network``s appears as a single edge in the resulting ``Network``,
          however the weight of the single edge is set to the SUM of the weights of the two individual
          edges that came from ``self`` and ``other``.

        If the two ``Networks`` have different numbers of nodes, we expand the adjacency matrix of the
        ``Network`` with fewer nodes to the same size of the ``Network`` with the most nodes, and fill in the
        new rows and columns with zeros. (Effectively, we treat the smaller ``Network`` as having no edges
        between the nodes that only exist in the larger ``Network``).

        Attempting to add a ``Network`` to a non-``Network`` object will throw a ``TypeError``.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        if not isinstance(other, Network):
            raise TypeError(
                f"Cannot non-Network instance ({type(other).__name__}) to a Network"
            )

        # Determine which Network has the most nodes, and thus which adjacency matrix needs to be "expanded".
        if other.n_nodes < self.n_nodes:
            larger = self
            smaller = other
        else:
            larger = other
            smaller = self

        # Expand the smaller adjacency matrix to match the size of the larger one.
        # Extra rows and columns that are added, contain only zeros.
        smaller_expanded_matrix = np.zeros(larger.adjacency_matrix.shape)
        smaller_expanded_matrix[: smaller.n_nodes, : smaller.n_nodes] = (
            smaller.adjacency_matrix
        )

        return Network(adj_mat=larger.adjacency_matrix + smaller_expanded_matrix)

    def __eq__(self, other: "Network") -> bool:
        """Compare two ``Networks`` for equality.

        ``Network``s are equal if and only if their adjacency matrices are
        identical.

        - Comparing a non-``Network`` object to a ``Network`` object
        returns ``False``.
        - Any potential subclassing of ``Network`` by ``self`` or ``other`` is
          ignored for the purposes of determining equality.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        return hasattr(other, "adjacency_matrix") and np.allclose(
            self.adjacency_matrix, other.adjacency_matrix
        )

    def __init__(self, *, adj_mat=None, edge_table=None) -> None:
        if adj_mat is None and edge_table is None:
            raise TubePlanningError("Provide either adjacency matrix or edge table.")
        if adj_mat is not None and edge_table is not None:
            raise TubePlanningError("Specify only one of adj_mat or edge_table.")

        if adj_mat is None:
            adj_mat = self._build_adj_from_edges(edge_table)

        matrix = np.asarray(adj_mat, dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise TubePlanningError("Adjacency matrix must be square.")
        if np.any(matrix < 0):
            raise TubePlanningError("Adjacency matrix must be non-negative.")

        # Zero diagonals for self-loop free graphs.
        np.fill_diagonal(matrix, 0.0)

        self.adjacency_matrix = matrix

    def __repr__(self):
        """Display information (e.g. via ``print``) for ``Network``s.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        return self.__str__()

    def __str__(self) -> str:
        """Display information (e.g. via ``print``) for ``Network``s.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        # Number of edges = number of non-zero entries in adjacency matrix / 2 (for symmetry).
        # Self-connecting edges are not allowed so we can't ever get 0.5 of an edge.
        n_edges = np.floor(np.sum(self.adjacency_matrix > 0) / 2.0).astype(int)
        return f"Network of {self.n_nodes} nodes and {n_edges} edges"

    def bfs(self, root):
        if root < 0 or root >= self.n_nodes:
            raise TubePlanningError("Root node out of bounds.")

        visited = np.zeros(self.n_nodes, dtype=bool)
        path_trace = np.full(self.n_nodes, -1, dtype=int)
        path_trace[root] = root
        queue = [root]
        visited[root] = True

        for current in queue:
            neighbours = np.nonzero(self.adjacency_matrix[current] > 0)[0]
            for nb in neighbours:
                if not visited[nb]:
                    visited[nb] = True
                    path_trace[nb] = current
                    queue.append(nb)
        return path_trace

    def capacity_constraint(self, flow):
        if not isinstance(flow, Flow):
            raise TypeError("flow must be a Flow instance.")
        if flow.flow_matrix.shape != self.adjacency_matrix.shape:
            raise TubePlanningError("Flow matrix and adjacency matrix shapes differ.")
        if not np.allclose(flow.flow_matrix, -flow.flow_matrix.T, atol=Flow._EPS):
            raise TubePlanningError("Flow matrix must be skew-symmetric.")
        if np.any(np.abs(flow.flow_matrix) - self.adjacency_matrix > Flow._EPS):
            raise TubePlanningError("Flow exceeds edge capacity.")
        return True

    def edmonds_karp(self, source, sink, maxiter=1000):
        if source == sink:
            raise TubePlanningError("Source and sink must differ.")
        if source < 0 or sink < 0 or source >= self.n_nodes or sink >= self.n_nodes:
            raise TubePlanningError("Source or sink out of bounds.")

        f = Flow.zero_flow(self.n_nodes, (source,), (sink,))
        converged = False

        for _ in range(maxiter):
            residual = Network(adj_mat=self.adjacency_matrix - f.flow_matrix)
            path_trace = residual.bfs(source)

            if path_trace[sink] < 0:
                converged = True
                break

            path = self.path_from_bfs(path_trace, sink)
            augment = min(
                residual.adjacency_matrix[i, j]
                for i, j in zip(path[:-1], path[1:], strict=True)
            )
            f.send_flow_along(path, augment)

        if not converged:
            raise TubePlanningError("Maximum iterations reached without convergence.")

        return f

    def maximum_flow(self, sources, sinks, maxiter=1000):
        sources = tuple(dict.fromkeys(int(s) for s in sources))
        sinks = tuple(dict.fromkeys(int(s) for s in sinks))

        if set(sources) & set(sinks):
            raise TubePlanningError("Sources and sinks must be disjoint.")
        if not sources or not sinks:
            raise TubePlanningError("Provide at least one source and one sink.")

        n = self.n_nodes
        total_capacity = float(np.sum(self.adjacency_matrix))
        if total_capacity <= 0:
            total_capacity = 1.0

        super_source = n
        super_sink = n + 1
        expanded = np.zeros((n + 2, n + 2), dtype=float)
        expanded[:n, :n] = self.adjacency_matrix

        for s in sources:
            if s < 0 or s >= n:
                raise TubePlanningError("Source index out of bounds.")
            expanded[super_source, s] = total_capacity
            expanded[s, super_source] = total_capacity
        for t in sinks:
            if t < 0 or t >= n:
                raise TubePlanningError("Sink index out of bounds.")
            expanded[t, super_sink] = total_capacity
            expanded[super_sink, t] = total_capacity

        expanded_net = Network(adj_mat=expanded)
        expanded_flow = expanded_net.edmonds_karp(super_source, super_sink, maxiter)

        base_flow = expanded_flow.flow_matrix[:n, :n]
        return Flow(base_flow, sources, sinks)

    def sufficient_flow(self, sources, sinks, maxiter=1000):
        # sources and sinks are expected to be mappings: node -> supply/demand
        if not sources or not sinks:
            raise TubePlanningError("Sources and sinks must be provided.")
        if any(val < 0 for val in sources.values()) or any(
            val < 0 for val in sinks.values()
        ):
            raise TubePlanningError("Supplies and demands must be non-negative.")

        n = self.n_nodes
        total_supply = float(sum(sources.values()))
        total_demand = float(sum(sinks.values()))
        if total_supply + Flow._EPS < total_demand:
            raise TubePlanningError("Insufficient total supply to meet demand.")

        super_source = n
        super_sink = n + 1
        expanded = np.zeros((n + 2, n + 2), dtype=float)
        expanded[:n, :n] = self.adjacency_matrix

        for node, capacity in sources.items():
            if node < 0 or node >= n:
                raise TubePlanningError("Source index out of bounds.")
            expanded[super_source, node] = capacity
            expanded[node, super_source] = capacity

        for node, capacity in sinks.items():
            if node < 0 or node >= n:
                raise TubePlanningError("Sink index out of bounds.")
            expanded[node, super_sink] = capacity
            expanded[super_sink, node] = capacity

        expanded_net = Network(adj_mat=expanded)
        expanded_flow = expanded_net.edmonds_karp(super_source, super_sink, maxiter)

        if expanded_flow.value + Flow._EPS < total_demand:
            raise TubePlanningError("Could not satisfy all demand.")

        base_flow = expanded_flow.flow_matrix[:n, :n]
        return Flow(base_flow, tuple(sources.keys()), tuple(sinks.keys()))

    @staticmethod
    def _build_adj_from_edges(edge_table):
        if edge_table is None:
            raise TubePlanningError("Edge table must not be None.")
        edges = list(edge_table)
        if not edges:
            raise TubePlanningError("Edge table is empty.")

        max_index = -1
        processed = []
        for entry in edges:
            if len(entry) != 3:
                raise TubePlanningError("Each edge must be a (u, v, weight) triple.")
            u, v, w = entry
            u, v, w = int(u), int(v), float(w)
            max_index = max(max_index, u, v)
            processed.append((u, v, w))

        size = max_index + 1
        adj = np.zeros((size, size), dtype=float)
        for u, v, w in processed:
            if u == v:
                continue
            adj[u, v] += w
            adj[v, u] += w
        return adj


def edmonds_karp(G, s, t, mi=1000):
    """Obtain the maximum flow from the `source` to the `sink` through this network.

    Maximal flow is computed using the Edmonds-Karp algorithm, which at each iteration
    considers the spare capacity graph (or "residual graph") and determines if a path
    from the source to the sink that is under the maximum capacity still exists. If such
    a path exists, we pass as much flow along that path as we can, update the spare
    capacity graph to reflect this additional flow, and then repeat until we have exhausted
    all possible paths that have spare capacity remaining.

    Args:
        G : Network
            Network on which to run Edmonds-Karp.
        s : int
            Index of the source node.
        t : int
            Index of the sink node.
        mi : int, default 1000
            Max number of iterations to perform.

    Returns:
        max_flow : Flow
            The maximum flow through the network; either the solution to the maximum flow
            problem or the best flow possible.

    Raises:
        TubePlanningError
    """
    f = Flow.zero_flow(G.n_nodes, (s,), (t,))
    c = False

    for _ in range(mi):
        rg = Network(adj_mat=G.adjacency_matrix - f.flow_matrix)
        pt = rg.bfs(s)

        if pt[t] < 0:
            c = True
            break

        p = G.path_from_bfs(pt, t)
        a = min(rg.adjacency_matrix[i, j] for i, j in zip(p[:-1], p[1:], strict=True))

        f.send_flow_along(p, a)

    if not c:
        raise TubePlanningError()

    return f
