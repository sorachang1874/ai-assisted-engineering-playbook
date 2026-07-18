from __future__ import annotations

import copy
import json
import pathlib
import unittest

from scripts.check_delivery_graph import validate


ROOT = pathlib.Path(__file__).resolve().parents[1]


class DeliveryGraphValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = json.loads(
            (ROOT / "examples/delivery-graph.json").read_text(encoding="utf-8")
        )

    def lane(self, lane_id: str) -> dict[str, object]:
        return next(lane for lane in self.graph["lanes"] if lane["id"] == lane_id)

    def test_example_is_valid_and_exposes_independent_ready_wave(self) -> None:
        errors, ready = validate(self.graph)

        self.assertEqual(errors, [])
        self.assertEqual(ready, ["distill-wave", "implement-filter-projection"])

    def test_runnable_lane_cannot_skip_incomplete_dependency(self) -> None:
        self.lane("promote-result-adapter")["status"] = "ready"

        errors, _ = validate(self.graph)

        self.assertTrue(
            any("runnable lane promote-result-adapter" in error for error in errors)
        )

    def test_canceled_dependency_does_not_unlock_downstream_lane(self) -> None:
        self.lane("review-result-adapter")["status"] = "canceled"

        _, ready = validate(self.graph)

        self.assertNotIn("promote-result-adapter", ready)

    def test_unordered_overlapping_writers_fail(self) -> None:
        self.lane("distill-wave")["writes"] = [
            "src/projection/filter_projection.py"
        ]

        errors, _ = validate(self.graph)

        self.assertTrue(
            any("unordered lanes overlap writes" in error for error in errors)
        )

    def test_gate_must_connect_review_to_promotion(self) -> None:
        self.lane("promote-result-adapter")["depends_on"] = [
            "freeze-result-owner"
        ]

        errors, _ = validate(self.graph)

        self.assertTrue(
            any("must depend on review lane" in error for error in errors)
        )

    def test_dependency_ordered_shared_write_requires_registered_hotspot(self) -> None:
        cleanup = copy.deepcopy(self.lane("distill-wave"))
        cleanup.update(
            {
                "id": "cleanup-contract",
                "status": "proposed",
                "depends_on": ["freeze-result-owner"],
                "reads": [],
                "writes": [
                    "docs/modules/agent-serving/contracts/result-owner.md"
                ],
                "hotspot_claims": [],
            }
        )
        self.graph["lanes"].append(cleanup)

        errors, _ = validate(self.graph)

        self.assertTrue(
            any("ordered overlapping writes lack a hotspot" in error for error in errors)
        )

    def test_registered_hotspot_allows_dependency_ordered_shared_write(self) -> None:
        cleanup = copy.deepcopy(self.lane("distill-wave"))
        cleanup.update(
            {
                "id": "cleanup-contract",
                "status": "proposed",
                "depends_on": ["freeze-result-owner"],
                "reads": [],
                "writes": [
                    "docs/modules/agent-serving/contracts/result-owner.md"
                ],
                "hotspot_claims": ["result-contract"],
            }
        )
        self.graph["lanes"].append(cleanup)
        self.lane("freeze-result-owner")["hotspot_claims"] = ["result-contract"]
        self.graph["hotspots"] = [
            {
                "id": "result-contract",
                "paths": [
                    "docs/modules/agent-serving/contracts/result-owner.md"
                ],
                "integration_owner": "lead",
                "writer_order": [
                    "freeze-result-owner",
                    "cleanup-contract",
                ],
                "release_condition": "Cleanup starts after contract freeze.",
            }
        ]

        errors, _ = validate(self.graph)

        self.assertEqual(errors, [])

    def test_malformed_path_list_fails_without_crashing(self) -> None:
        self.lane("distill-wave")["writes"] = "docs/not-a-list.md"

        errors, _ = validate(self.graph)

        self.assertTrue(
            any("distill-wave.writes must be a string list" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
