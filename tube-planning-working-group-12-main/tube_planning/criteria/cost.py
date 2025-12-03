from typing import Literal, TypeAlias

from tube_planning.criteria.base import Criteria
from tube_planning._exceptions import TubePlanningError
import math
import numpy as np

COST_NAMES = sorted(["infra", "staff", "vehic"])
CostTypes: TypeAlias = Literal["infra", "staff", "total", "vehic"]


class CostCriteria(Criteria):

    def __init__(self, costs, budget=0, *, description="", weight=1.0):
        super().__init__(description=description, weight=weight)
        if isinstance(costs, str):
            costs = [costs]
        self.costs = sorted(set(c.lower() for c in costs))
        valid = set(COST_NAMES + ["total"])
        if not self.costs or any(c not in valid for c in self.costs):
            raise TubePlanningError(
                f"Costs must be subset of {valid}, got {self.costs!r}."
            )
        self.budget = float(budget)

    def _evaluate(
        self,
        proposed,
        current,
        costing_information,
    ):
        if costing_information is None:
            raise TubePlanningError("Costing information required for cost criteria.")
        required_keys = {"new", "ext", "hire", "train"}
        if not required_keys.issubset(costing_information.keys()):
            missing = required_keys - set(costing_information.keys())
            raise TubePlanningError(f"Missing fixed cost entries: {missing}")

        c_new = float(costing_information["new"])
        c_ext = float(costing_information["ext"])
        c_hire = float(costing_information["hire"])
        c_train = float(costing_information["train"])

        cur = current.adjacency_matrix
        prop = proposed.adjacency_matrix
        size = max(cur.shape[0], prop.shape[0])
        cur_exp = np.zeros((size, size))
        prop_exp = np.zeros((size, size))
        cur_exp[: cur.shape[0], : cur.shape[1]] = cur
        prop_exp[: prop.shape[0], : prop.shape[1]] = prop

        # Infrastructure cost
        added_edges = 0
        existing_edges = 0
        for i in range(size):
            for j in range(i + 1, size):
                if prop_exp[i, j] > 0:
                    if cur_exp[i, j] > 0:
                        existing_edges += 1
                    else:
                        added_edges += 1
        c_infra = added_edges * c_new + existing_edges * c_ext

        # Staffing cost (per node new edge count)
        c_staff = 0.0
        for i in range(size):
            new_edges = 0
            for j in range(size):
                if i == j:
                    continue
                if prop_exp[i, j] > 0 and cur_exp[i, j] == 0:
                    new_edges += 1
            if new_edges > 0:
                c_staff += c_hire * math.sqrt(new_edges)

        # Vehicle cost based on max proposed edge weight
        w_max = float(np.max(prop)) if prop.size > 0 else 0.0
        c_vehic = 24 * w_max * c_train

        total_cost = 0.0
        if "total" in self.costs:
            total_cost = c_infra + c_staff + c_vehic
        else:
            if "infra" in self.costs:
                total_cost += c_infra
            if "staff" in self.costs:
                total_cost += c_staff
            if "vehic" in self.costs:
                total_cost += c_vehic

        return self.budget - total_cost

    def to_json_part(self) -> dict[str, bool | float | list[str] | str]:
        """Convert this ``Criteria`` to a dictionary.

        A dictionary can be saved to a `json` file, or used as part of an entry in
        a larger dictionary that is to be saved to a `json` file.

        The dictionary that is returned has keys that correspond to the class
        names of the class's attributes (``str``). The value of these keys is the
        value of the corresponding instance attribute at the time of calling this
        method.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        return {**super().to_json_part(), "costs": self.costs, "budget": self.budget}
