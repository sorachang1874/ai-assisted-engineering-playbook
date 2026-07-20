#!/usr/bin/env python3
"""Validate delivery dependencies, write ownership, and gate edges."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


STATUSES = {"proposed", "ready", "active", "blocked", "done", "canceled"}
GATE_MODES = {"none", "async_before_promotion", "blocking_before_execution"}
LANE_FIELDS = {
    "id", "kind", "owner", "status", "depends_on", "blocked_by", "reads",
    "writes", "hotspot_claims", "deliverable", "validation", "stop_condition",
    "handoff_path", "gate",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def strings(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty(item) for item in value)


def normalize_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    return value.removeprefix("./").rstrip("/")


def valid_path(value: str) -> bool:
    value = normalize_path(value)
    non_tree = value.removesuffix("/**")
    parts = pathlib.PurePosixPath(non_tree).parts
    return (
        bool(value)
        and not value.startswith("/")
        and ".." not in parts
        and "*" not in non_tree
    )


def paths_overlap(left: str, right: str) -> bool:
    left, right = normalize_path(left), normalize_path(right)
    left_tree, right_tree = left.endswith("/**"), right.endswith("/**")
    left_base = left[:-3].rstrip("/") if left_tree else left
    right_base = right[:-3].rstrip("/") if right_tree else right
    return (
        left_base == right_base
        or (left_tree and right_base.startswith(left_base + "/"))
        or (right_tree and left_base.startswith(right_base + "/"))
    )


def any_overlap(left: list[str], right: list[str]) -> bool:
    return any(paths_overlap(a, b) for a in left for b in right)


def validate(data: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    ready: list[str] = []
    if not isinstance(data, dict):
        return ["root must be an object"], ready
    if data.get("schema_version") != "delivery_graph.v1":
        errors.append("schema_version must equal 'delivery_graph.v1'")
    for field in ("run_id", "objective", "integration_owner", "graph_owner_path"):
        if not nonempty(data.get(field)):
            errors.append(f"root.{field} must be a non-empty string")
    if nonempty(data.get("graph_owner_path")) and not valid_path(data["graph_owner_path"]):
        errors.append("graph_owner_path must be repository-relative")

    distill = data.get("distillation")
    if not isinstance(distill, dict):
        errors.append("distillation must be an object")
    else:
        for field in ("owner", "candidate_path"):
            if not nonempty(distill.get(field)):
                errors.append(f"distillation.{field} must be a non-empty string")
        if not strings(distill.get("cadence")) or not distill.get("cadence"):
            errors.append("distillation.cadence must be a non-empty string list")

    raw_lanes = data.get("lanes")
    if not isinstance(raw_lanes, list) or not raw_lanes:
        return errors + ["lanes must be a non-empty list"], ready
    lanes: dict[str, dict[str, Any]] = {}
    for index, lane in enumerate(raw_lanes):
        if not isinstance(lane, dict):
            errors.append(f"lanes[{index}] must be an object")
            continue
        missing = sorted(LANE_FIELDS - lane.keys())
        if missing:
            errors.append(f"lanes[{index}] missing: {', '.join(missing)}")
        lane_id = lane.get("id")
        if not nonempty(lane_id):
            errors.append(f"lanes[{index}].id must be non-empty")
            continue
        if lane_id in lanes:
            errors.append(f"duplicate lane id: {lane_id}")
            continue
        lanes[lane_id] = lane
        for field in ("kind", "owner", "deliverable", "stop_condition", "handoff_path"):
            if not nonempty(lane.get(field)):
                errors.append(f"lane {lane_id}.{field} must be non-empty")
        if lane.get("status") not in STATUSES:
            errors.append(f"lane {lane_id}.status is invalid")
        for field in (
            "depends_on",
            "blocked_by",
            "reads",
            "writes",
            "hotspot_claims",
            "validation",
        ):
            if not strings(lane.get(field)):
                errors.append(f"lane {lane_id}.{field} must be a string list")
        for field in ("reads", "writes"):
            paths = lane.get(field)
            if isinstance(paths, list):
                for path in paths:
                    if isinstance(path, str) and not valid_path(path):
                        errors.append(f"lane {lane_id} has invalid path: {path!r}")
        if not lane.get("validation"):
            errors.append(f"lane {lane_id}.validation must not be empty")
        if (lane.get("status") == "blocked") != bool(lane.get("blocked_by")):
            errors.append(f"lane {lane_id}.blocked_by must be non-empty exactly when blocked")
        gate = lane.get("gate")
        if not isinstance(gate, dict) or set(gate) != {"mode", "review_lane", "protected_lanes"}:
            errors.append(f"lane {lane_id}.gate has an invalid shape")
        elif (
            gate.get("mode") not in GATE_MODES
            or not isinstance(gate.get("review_lane"), str)
            or not strings(gate.get("protected_lanes"))
        ):
            errors.append(f"lane {lane_id}.gate has invalid values")

    lane_ids = set(lanes)
    for lane_id, lane in lanes.items():
        unknown = sorted(set(lane.get("depends_on", [])) - lane_ids)
        if unknown:
            errors.append(f"lane {lane_id} has unknown dependencies: {', '.join(unknown)}")
        if lane_id in lane.get("depends_on", []):
            errors.append(f"lane {lane_id} depends on itself")

    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(lane_id: str, trail: tuple[str, ...]) -> None:
        if lane_id in visiting:
            errors.append(f"dependency cycle: {' -> '.join((*trail, lane_id))}")
            return
        if lane_id in visited:
            return
        visiting.add(lane_id)
        for dependency in lanes[lane_id].get("depends_on", []):
            if dependency in lanes:
                walk(dependency, (*trail, lane_id))
        visiting.remove(lane_id)
        visited.add(lane_id)

    for lane_id in lanes:
        walk(lane_id, ())

    ancestors: dict[str, set[str]] = {}

    def get_ancestors(lane_id: str, seen: set[str] | None = None) -> set[str]:
        if lane_id in ancestors:
            return ancestors[lane_id]
        seen = set() if seen is None else seen
        if lane_id in seen:
            return set()
        result: set[str] = set()
        for dependency in lanes[lane_id].get("depends_on", []):
            if dependency in lanes:
                result.add(dependency)
                result.update(get_ancestors(dependency, seen | {lane_id}))
        ancestors[lane_id] = result
        return result

    for lane_id in lanes:
        get_ancestors(lane_id)
    for lane_id, lane in lanes.items():
        incomplete = [
            dependency
            for dependency in lane.get("depends_on", [])
            if dependency in lanes and lanes[dependency].get("status") != "done"
        ]
        if lane.get("status") in {"ready", "active"} and incomplete:
            errors.append(
                f"runnable lane {lane_id} has incomplete dependencies: "
                f"{', '.join(incomplete)}"
            )
        if (
            lane.get("status") in {"proposed", "ready"}
            and not incomplete
            and not lane.get("blocked_by")
        ):
            ready.append(lane_id)

    raw_hotspots = data.get("hotspots")
    if not isinstance(raw_hotspots, list):
        errors.append("hotspots must be a list")
        raw_hotspots = []
    hotspots: dict[str, dict[str, Any]] = {}
    hotspot_fields = {"id", "paths", "integration_owner", "writer_order", "release_condition"}
    for index, hotspot in enumerate(raw_hotspots):
        if not isinstance(hotspot, dict) or set(hotspot) != hotspot_fields:
            errors.append(f"hotspots[{index}] has an invalid shape")
            continue
        hotspot_id = hotspot.get("id")
        if not nonempty(hotspot_id) or hotspot_id in hotspots:
            errors.append(f"hotspots[{index}] has an empty or duplicate id")
            continue
        hotspots[hotspot_id] = hotspot
        if (
            not strings(hotspot.get("paths"))
            or not hotspot.get("paths")
            or not strings(hotspot.get("writer_order"))
            or not hotspot.get("writer_order")
        ):
            errors.append(
                f"hotspot {hotspot_id} paths/writer_order must be non-empty "
                "string lists"
            )
        for path in hotspot.get("paths", []):
            if isinstance(path, str) and not valid_path(path):
                errors.append(f"hotspot {hotspot_id} has invalid path: {path!r}")
        if not nonempty(hotspot.get("integration_owner")) or not nonempty(
            hotspot.get("release_condition")
        ):
            errors.append(f"hotspot {hotspot_id} must name owner and release condition")
        writers = hotspot.get("writer_order", [])
        if len(writers) != len(set(writers)) or set(writers) - lane_ids:
            errors.append(f"hotspot {hotspot_id} has duplicate or unknown writers")
        for earlier, later in zip(writers, writers[1:]):
            if earlier in lanes and later in lanes and earlier not in ancestors[later]:
                errors.append(
                    f"hotspot {hotspot_id} is not dependency-ordered: "
                    f"{earlier} -> {later}"
                )
        for writer in writers:
            if writer in lanes and not any_overlap(
                lanes[writer].get("writes", []), hotspot.get("paths", [])
            ):
                errors.append(f"hotspot {hotspot_id} writer {writer} has no overlapping write")
            if writer in lanes and hotspot_id not in lanes[writer].get("hotspot_claims", []):
                errors.append(f"hotspot {hotspot_id} writer {writer} does not claim it")

    for lane_id, lane in lanes.items():
        claims = set(lane.get("hotspot_claims", []))
        if claims - set(hotspots):
            errors.append(f"lane {lane_id} claims unknown hotspots")
        for claim in claims & set(hotspots):
            if lane_id not in hotspots[claim].get("writer_order", []):
                errors.append(f"lane {lane_id} claims hotspot {claim} but is not a writer")

    lane_items = list(lanes.items())
    for index, (left_id, left) in enumerate(lane_items):
        for right_id, right in lane_items[index + 1:]:
            if not any_overlap(left.get("writes", []), right.get("writes", [])):
                continue
            if left_id not in ancestors[right_id] and right_id not in ancestors[left_id]:
                errors.append(f"unordered lanes overlap writes: {left_id}, {right_id}")
                continue
            covered = any(
                left_id in spot.get("writer_order", [])
                and right_id in spot.get("writer_order", [])
                and any_overlap(left.get("writes", []), spot.get("paths", []))
                and any_overlap(right.get("writes", []), spot.get("paths", []))
                for spot in hotspots.values()
            )
            if not covered:
                errors.append(f"ordered overlapping writes lack a hotspot: {left_id}, {right_id}")

    for lane_id, lane in lanes.items():
        gate = lane.get("gate")
        if not isinstance(gate, dict):
            continue
        mode = gate.get("mode")
        reviewer = gate.get("review_lane")
        protected = gate.get("protected_lanes")
        if mode == "none":
            if reviewer or protected:
                errors.append(f"lane {lane_id} gate none must not name review/protected lanes")
            continue
        if not nonempty(reviewer) or reviewer not in lanes:
            errors.append(f"lane {lane_id} gate must name an existing review lane")
            continue
        if lanes[reviewer].get("kind") != "review":
            errors.append(f"lane {lane_id} gate target {reviewer} must have kind review")
        if lane_id not in ancestors[reviewer]:
            errors.append(f"review lane {reviewer} must depend on gated lane {lane_id}")
        if not protected:
            errors.append(f"lane {lane_id} gate must name protected lanes")
        for target in protected or []:
            if target not in lanes:
                errors.append(f"lane {lane_id} gate has unknown protected lane {target}")
            elif reviewer not in ancestors[target]:
                errors.append(f"protected lane {target} must depend on review lane {reviewer}")
    return errors, sorted(set(ready))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=pathlib.Path)
    parser.add_argument("--ready", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.graph.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"delivery graph read failed: {exc}", file=sys.stderr)
        return 1
    errors, ready = validate(data)
    if errors:
        for error in errors:
            print(f"delivery graph error: {error}", file=sys.stderr)
        return 1
    print(f"delivery graph valid: {len(data['lanes'])} lanes, {len(data['hotspots'])} hotspots")
    if args.ready:
        print("ready lanes: " + (", ".join(ready) if ready else "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
