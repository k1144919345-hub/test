from tube_planning.criteria.base import Criteria
from tube_planning._exceptions import TubePlanningError
from tube_planning.networks.network import Network


class PerformanceCriteria(Criteria):

    @property
    def is_sufficient_problem(self) -> bool:
        """Whether this criteria examines a sufficient flow problem (True)
        or a maximum flow problem (False).

        THIS PROPERTY IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        return self.supplies is not None and self.demands is not None

    def __init__(self, sources, sinks, supplies, demands, *, description, weight):
        super().__init__(description=description, weight=weight)
        self.sources = [int(s) for s in sources]
        self.sinks = [int(s) for s in sinks]
        self.supplies = None if supplies is None else [float(x) for x in supplies]
        self.demands = None if demands is None else [float(x) for x in demands]

        if not self.sources or not self.sinks:
            raise TubePlanningError("At least one source and one sink required.")
        if self.is_sufficient_problem:
            if len(self.sources) != len(self.supplies) or len(self.sinks) != len(
                self.demands
            ):
                raise TubePlanningError("Supplies/demands must align with sources/sinks.")
            if any(v < 0 for v in self.supplies + self.demands):
                raise TubePlanningError("Supplies and demands must be non-negative.")

    def _evaluate(self, proposed, current, *args, **kwargs):
        combined = current + proposed
        try:
            if self.is_sufficient_problem:
                source_caps = dict(zip(self.sources, self.supplies, strict=True))
                sink_caps = dict(zip(self.sinks, self.demands, strict=True))
                flow = combined.sufficient_flow(source_caps, sink_caps)
                return 1.0 if flow.value >= sum(self.demands) else -1.0

            # Maximum flow improvement on combined vs current
            combined_flow = combined.maximum_flow(self.sources, self.sinks)
            current_flow = current.maximum_flow(self.sources, self.sinks)
            return combined_flow.value - current_flow.value
        except TubePlanningError:
            return -1.0

    def to_json_part(self) -> dict[str, bool | float | str | list[int] | list[float]]:
        """Convert this ``Criteria`` to a dictionary.

        A dictionary can be saved to a `json` file, or used as part of an entry in
        a larger dictionary that is to be saved to a `json` file.

        The dictionary that is returned has keys that correspond to the class
        names of the class's attributes (``str``). The value of these keys is the
        value of the corresponding instance attribute at the time of calling this
        method.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        all_attributes = {
            **super().to_json_part(),
            "sources": self.sources,
            "sinks": self.sinks,
        }
        if self.is_sufficient_problem:
            all_attributes["supplies"] = self.supplies
            all_attributes["demands"] = self.demands
        return all_attributes
