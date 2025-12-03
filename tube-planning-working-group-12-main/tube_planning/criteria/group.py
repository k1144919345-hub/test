from typing import Iterable
from pathlib import Path
import json

from tube_planning.criteria.base import Criteria
from tube_planning.criteria.cost import CostCriteria
from tube_planning.criteria.performance import PerformanceCriteria
from tube_planning._exceptions import TubePlanningError


class CriteriaGroup:

    @classmethod
    def from_file(cls, fpath):
        with open(fpath, "r") as f:
            data = json.load(f)

        def parse_criteria(item):
            if "costs" in item and "budget" in item:
                return CriteriaFactory.cost(item)
            if "sources" in item and "sinks" in item:
                return CriteriaFactory.performance(item)
            raise TubePlanningError("Unknown criteria specification.")

        essential = [parse_criteria(c) for c in data.get("essential", [])]
        desirable = [parse_criteria(c) for c in data.get("desirable", [])]
        return cls(desirable=desirable, essential=essential)

    def __init__(
        self,
        *,
        desirable: Iterable[Criteria] = (),
        essential: Iterable[Criteria] = (),
    ):
        """Create a new CriteriaGroup from a list of essential and desirable ``Criteria``.

        Args:
            desirable : Iterable[Criteria]
                Collection of ``Criteria`` objects to be considered desirable.
            essential : Iterable[Criteria]
                Collection of ``Criteria`` objects to be considered essential.

        THIS METHOD IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
        """
        self.desirable = list(desirable)
        self.essential = list(essential)

    def evaluate(
        self,
        proposed,
        current,
        costing_information,
    ):
        score = 0.0
        failed = []
        for crit in self.essential:
            val = crit.evaluate(proposed, current, costing_information)
            if val <= 0:
                failed.append(crit)
            score += val
        for crit in self.desirable:
            score += crit.evaluate(proposed, current, costing_information)
        return score, failed

    def to_criteria_file(self, fpath: Path) -> None:
        """Save the instance as a criteria file.

        Criteria files are ``json`` files that contain two keys, 'essential' and
        'desirable'. The values of each of these keys is a list of items, with each
        item specifying a ``Criteria``.

        Args:
            fpath : Path
                Path to save criteria file to.

        THIS METHOD IS PROVIDED TO YOU - do not make functional edits to it.
        YOU WILL BE REQUIRED TO WRITE TESTS FOR THIS METHOD.
        """
        json_dict = {}
        json_dict["essential"] = [c.to_json_part() for c in self.essential]
        json_dict["desirable"] = [c.to_json_part() for c in self.desirable]

        with open(fpath, "w") as json_file:
            json.dump(json_dict, json_file)


class CriteriaFactory:
    """Helper factory to build criteria objects from dict specs."""

    @staticmethod
    def cost(item):
        return CostCriteria(
            costs=item["costs"],
            budget=item["budget"],
            description=item.get("description", ""),
            weight=item.get("weight", 1.0),
        )

    @staticmethod
    def performance(item):
        return PerformanceCriteria(
            item["sources"],
            item["sinks"],
            item.get("supplies"),
            item.get("demands"),
            description=item.get("description", ""),
            weight=item.get("weight", 1.0),
        )
