#!/usr/bin/env python3
"""Validate the machine-readable header of a session task packet."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "session_task_packet_v1"
READY_STATUSES = {"ready", "claimed"}
ALLOWED_STATUSES = READY_STATUSES | {
    "blocked",
    "handoff",
    "integrated",
    "retired",
    "superseded",
}
PLACEHOLDER_RE = re.compile(
    r"(?:<[^>]+>|\b(?:TBD|TODO|TO_FILL|CHANGEME)\b)", re.IGNORECASE
)
COMMIT_RE = re.compile(r"[0-9a-f]{40}")


def _extract_header(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
    if match is None:
        raise ValueError("missing JSON header fence")
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("JSON header must be an object")
    return value


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return PLACEHOLDER_RE.search(value) is not None
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    return False


def _commit_exists(repository: str, commit: str) -> bool:
    result = subprocess.run(
        ["git", "-C", repository, "cat-file", "-e", f"{commit}^{{commit}}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def _artifact_exists(repository: str, artifact: str) -> bool:
    path = Path(artifact)
    if not path.is_absolute():
        path = Path(repository) / path
    return path.is_file()


def validate_packet(header: dict[str, Any], *, require_ready: bool) -> list[str]:
    errors: list[str] = []
    if header.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    status = header.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUSES)}")
    if require_ready and status not in READY_STATUSES:
        errors.append("--ready requires status ready or claimed")

    for field in (
        "packet_id",
        "repository",
        "branch",
        "worktree",
        "integration_owner",
        "handoff_path",
    ):
        if not _nonempty_string(header.get(field)):
            errors.append(f"{field} must be a non-empty string")

    packet_version = header.get("packet_version")
    if type(packet_version) is not int or packet_version < 1:
        errors.append("packet_version must be an integer >= 1")

    base_commit = header.get("base_commit")
    if require_ready:
        if not isinstance(base_commit, str) or COMMIT_RE.fullmatch(base_commit) is None:
            errors.append(
                "ready packet base_commit must be exactly 40 lowercase hex characters"
            )
        elif _nonempty_string(header.get("repository")) and not _commit_exists(
            header["repository"], base_commit
        ):
            errors.append("base_commit does not exist in repository")

    lease = header.get("lease")
    if not isinstance(lease, dict):
        errors.append("lease must be an object")
    else:
        for field in ("owner", "issued_at", "revalidate_after"):
            if not _nonempty_string(lease.get(field)):
                errors.append(f"lease.{field} must be a non-empty string")
        for field in ("read_paths", "write_paths"):
            values = lease.get(field)
            if (
                not isinstance(values, list)
                or not values
                or not all(_nonempty_string(item) for item in values)
            ):
                errors.append(f"lease.{field} must be a non-empty string list")

    dependencies = header.get("dependencies")
    if not isinstance(dependencies, list):
        errors.append("dependencies must be a list")
    else:
        for index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict) or not _nonempty_string(
                dependency.get("id")
            ):
                errors.append(f"dependencies[{index}] must have a non-empty id")
                continue
            if require_ready:
                if dependency.get("status") != "satisfied":
                    errors.append(f"dependencies[{index}] is not satisfied")
                evidence_commit = dependency.get("evidence_commit")
                evidence_artifact = dependency.get("evidence_artifact")
                valid_commit = (
                    isinstance(evidence_commit, str)
                    and COMMIT_RE.fullmatch(evidence_commit) is not None
                )
                valid_artifact = _nonempty_string(evidence_artifact)
                if not valid_commit and not valid_artifact:
                    errors.append(
                        f"dependencies[{index}] needs a full evidence_commit or evidence_artifact"
                    )
                repository = header.get("repository")
                if (
                    valid_commit
                    and _nonempty_string(repository)
                    and not _commit_exists(repository, evidence_commit)
                ):
                    errors.append(
                        f"dependencies[{index}] evidence_commit does not exist"
                    )
                if (
                    valid_artifact
                    and _nonempty_string(repository)
                    and not _artifact_exists(repository, evidence_artifact)
                ):
                    errors.append(
                        f"dependencies[{index}] evidence_artifact does not exist"
                    )

    hotspots = header.get("hotspots")
    if not isinstance(hotspots, list):
        errors.append("hotspots must be a list")
    else:
        for index, hotspot in enumerate(hotspots):
            if not isinstance(hotspot, dict):
                errors.append(f"hotspots[{index}] must be an object")
                continue
            for field in ("id", "current_writer", "release_evidence"):
                if not _nonempty_string(hotspot.get(field)):
                    errors.append(
                        f"hotspots[{index}].{field} must be a non-empty string"
                    )
            position = hotspot.get("writer_position")
            if type(position) is not int or position < 1:
                errors.append(
                    f"hotspots[{index}].writer_position must be an integer >= 1"
                )

    validation = header.get("validation")
    if not isinstance(validation, list) or not validation:
        errors.append("validation must be a non-empty list")
    else:
        for index, check in enumerate(validation):
            if not isinstance(check, dict):
                errors.append(f"validation[{index}] must be an object")
                continue
            for field in ("command", "expected"):
                if not _nonempty_string(check.get(field)):
                    errors.append(
                        f"validation[{index}].{field} must be a non-empty string"
                    )

    review = header.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
    else:
        if not _nonempty_string(review.get("mode")):
            errors.append("review.mode must be a non-empty string")
        if not isinstance(review.get("required_before"), list):
            errors.append("review.required_before must be a list")
        if not isinstance(review.get("may_continue_without_verdict"), list):
            errors.append("review.may_continue_without_verdict must be a list")

    stale_if = header.get("stale_if")
    if (
        not isinstance(stale_if, list)
        or not stale_if
        or not all(_nonempty_string(item) for item in stale_if)
    ):
        errors.append("stale_if must be a non-empty string list")

    if require_ready and _contains_placeholder(header):
        errors.append("ready packet contains a placeholder")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument(
        "--ready",
        action="store_true",
        help="require a dispatchable ready/claimed packet and verify its base commit",
    )
    args = parser.parse_args()
    try:
        header = _extract_header(args.packet)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    errors = validate_packet(header, require_ready=args.ready)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {header['packet_id']} status={header['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
