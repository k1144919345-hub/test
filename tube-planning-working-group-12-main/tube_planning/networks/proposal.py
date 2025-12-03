from tube_planning.networks.network import Network

from tube_planning._exceptions import TubePlanningError
import csv


class Proposal(Network):

    _all_proposals: list["Proposal"] = []

    @property
    def names_in_use(self) -> tuple[str]:
        """Return a tuple of all ``Proposal`` names currently in use."""
        return tuple(p.name for p in Proposal._all_proposals)

    @classmethod
    def from_file(cls, csv_file, weights_are_travel_times, name):
        edge_table = []
        with open(csv_file, newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not row:
                    continue
                try:
                    u, v, weight = int(row[0]), int(row[1]), float(row[2])
                except (ValueError, IndexError):
                    # Skip rows that cannot be parsed (e.g. headers)
                    continue
                edge_table.append((u, v, weight))

        if not edge_table:
            raise TubePlanningError("No edges found in proposal file.")

        return cls(name, edge_table=edge_table)

    def __init__(self, name: str, *, adj_mat=None, edge_table=None):
        if name in self.names_in_use:
            raise TubePlanningError(f"Proposal name '{name}' already in use.")

        self.name = str(name)
        super().__init__(adj_mat=adj_mat, edge_table=edge_table)
        Proposal._all_proposals.append(self)

    def __str__(self):
        """Display information (e.g. via ``print``) for ``Proposal``s.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        return super().__str__().replace("Network", f"Proposal ({self.name})")
