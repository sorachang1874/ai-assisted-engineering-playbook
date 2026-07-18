from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_session_packet import validate_packet


REPOSITORY = Path(__file__).resolve().parents[1]
HEAD = subprocess.run(
    ["git", "-C", str(REPOSITORY), "rev-parse", "HEAD"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()


def _header() -> dict[str, object]:
    return {
        "schema_version": "session_task_packet_v1",
        "packet_id": "run-lane-v1",
        "packet_version": 1,
        "status": "ready",
        "repository": str(REPOSITORY),
        "base_commit": HEAD,
        "branch": "codex/run-lane",
        "worktree": "/tmp/run-lane",
        "integration_owner": "lead",
        "handoff_path": ".coord/handoffs/run-lane-v1.md",
        "lease": {
            "owner": "lane-owner",
            "issued_at": "2026-07-18T00:00:00Z",
            "revalidate_after": "2026-07-19T00:00:00Z",
            "read_paths": ["docs/contract.md"],
            "write_paths": ["src/owner.py"],
        },
        "dependencies": [
            {
                "id": "contract",
                "status": "satisfied",
                "evidence_commit": HEAD,
                "evidence_artifact": None,
            }
        ],
        "hotspots": [
            {
                "id": "owner-registry",
                "writer_position": 1,
                "current_writer": "run-lane",
                "release_evidence": "commit plus targeted tests",
            }
        ],
        "validation": [{"command": "pytest -q test_owner.py", "expected": "1 passed"}],
        "review": {
            "mode": "pinned-independent",
            "required_before": ["promotion"],
            "may_continue_without_verdict": ["unrelated-lane"],
        },
        "stale_if": ["base commit is superseded"],
    }


def test_ready_packet_is_valid() -> None:
    assert validate_packet(_header(), require_ready=True) == []


def test_ready_packet_rejects_placeholder_and_unsatisfied_dependency() -> None:
    header = _header()
    header["branch"] = "codex/<run>-lane"
    dependencies = header["dependencies"]
    assert isinstance(dependencies, list)
    dependencies[0]["status"] = "blocked"
    errors = validate_packet(header, require_ready=True)
    assert "dependencies[0] is not satisfied" in errors
    assert "ready packet contains a placeholder" in errors


def test_blocked_packet_may_leave_base_unresolved() -> None:
    header = _header()
    header["status"] = "blocked"
    header["base_commit"] = None
    dependencies = header["dependencies"]
    assert isinstance(dependencies, list)
    dependencies[0]["status"] = "blocked"
    dependencies[0]["evidence_commit"] = None
    assert validate_packet(header, require_ready=False) == []


def test_ready_packet_rejects_missing_dependency_evidence() -> None:
    header = _header()
    dependencies = header["dependencies"]
    assert isinstance(dependencies, list)
    dependencies[0]["evidence_commit"] = "0" * 40
    dependencies[0]["evidence_artifact"] = "missing-review.md"
    errors = validate_packet(header, require_ready=True)
    assert "dependencies[0] evidence_commit does not exist" in errors
    assert "dependencies[0] evidence_artifact does not exist" in errors


def test_cli_reads_first_json_fence(tmp_path: Path) -> None:
    packet = tmp_path / "packet.md"
    packet.write_text(
        "# Packet\n\n```json\n" + json.dumps(_header()) + "\n```\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(REPOSITORY / "scripts" / "check_session_packet.py"),
            str(packet),
            "--ready",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "VALID: run-lane-v1 status=ready" in result.stdout
