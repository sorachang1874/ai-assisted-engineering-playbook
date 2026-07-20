# Session Task Packet

The first JSON block is machine-readable. Copy the template, replace every
placeholder, and run `python scripts/check_session_packet.py <packet> --ready`
before dispatch. A blocked packet may omit unresolved evidence only while
`status` is `blocked`.

```json
{
  "schema_version": "session_task_packet_v1",
  "packet_id": "<run>-<lane>-v1",
  "packet_version": 1,
  "status": "blocked",
  "repository": "/absolute/path/to/repository",
  "base_commit": null,
  "branch": "codex/<run>-<lane>",
  "worktree": "/absolute/path/to/independent-worktree",
  "integration_owner": "<owner>",
  "handoff_path": ".coord/handoffs/<lane>-v1.md",
  "lease": {
    "owner": "<session-owner>",
    "issued_at": "<ISO-8601>",
    "revalidate_after": "<ISO-8601>",
    "read_paths": ["path/to/context.md"],
    "write_paths": ["path/to/exclusive/file.py"]
  },
  "dependencies": [
    {
      "id": "<dependency-lane>",
      "status": "blocked",
      "evidence_commit": null,
      "evidence_artifact": null
    }
  ],
  "hotspots": [
    {
      "id": "<hotspot-id>",
      "writer_position": 1,
      "current_writer": "<lane-or-none>",
      "release_evidence": "<commit-and-check>"
    }
  ],
  "validation": [
    {
      "command": "<exact command>",
      "expected": "<literal count or invariant>"
    }
  ],
  "review": {
    "mode": "pinned-independent",
    "required_before": ["<promotion-or-live-edge>"],
    "may_continue_without_verdict": ["<unrelated-lane-or-none>"]
  },
  "stale_if": [
    "base commit is superseded",
    "dependency evidence changes",
    "another diff enters a leased write path",
    "hotspot writer order changes",
    "revalidate_after passes without lead revalidation"
  ]
}
```

## Goal and Deliverable

- User-visible or operator capability this lane advances:
- Concrete lane deliverable:
- Downstream graph node unblocked:

## Required Context

Read in order. Cite exact commits or immutable artifacts when semantics matter.

1.

## Contract and Decision Boundaries

- Frozen inputs this lane may consume:
- Questions this lane must answer:
- Values this lane must not invent (schema/version/owner/relation/predicate):
- Residual-ledger rows retained:

## Worktree Preflight

```sh
git -C <repository> cat-file -e <base_commit>^{commit}
git -C <worktree> rev-parse HEAD
git -C <worktree> status --short
```

Require `HEAD == base_commit` before the first edit. Do not reset, stash, or
adopt another session's dirty files to force that equality.

## Implementation or Analysis Instructions

1.

## Stop Conditions

Stop and hand back to the integration owner if:

- a dependency is not at the packet's evidence commit;
- a required write is outside `lease.write_paths`;
- another writer occupies a leased path or the lane's hotspot turn is inactive;
- a schema, owner, relation, migration, served predicate, destructive action,
  credential, or live-cost decision would have to be guessed; or
- the packet is stale by any `stale_if` rule.

## Handoff Contract

Report base/head, changed files, exact commands with counts/durations, skipped
checks, review state, deviations, residual risks, negative evidence, stale
packet check, and the exact next graph node. The lane owner does not mark
integration, promotion, or live readiness complete.
