# Contract-First Development

## Why Contracts Drift

Contract drift usually appears when multiple modules independently derive a similar field:

- One endpoint derives count from a fast local event.
- Another reads from a canonical projection.
- A worker writes a compatibility pointer.
- A UI falls back to an older summary.
- A metric pairs unrelated events by timestamp.

Small tests often pass because all paths finish at roughly the same time. Larger or slower runs expose the drift.

## Owner Matrix

Every shared contract should have an owner matrix:

| Field | Owner | Source of truth | Allowed values | Derivation | Consumers | Fallback | Deletion condition | Preflight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `status` | lifecycle owner | current-state table | queued/running/completed/failed | reducer output | API/UI/metrics | none | old summary retired | status parity test |

See `examples/contract-owner-matrix.md`.

## Contract Change Checklist

Before implementation:

- Define owner and source of truth.
- Identify all producers.
- Identify all consumers.
- Decide whether old sources are migration-only or removed.
- Define expected behavior during partial progress.
- Define failure and retry semantics.

During implementation:

- Centralize derivation in one module.
- Update all public endpoints or workers that expose it.
- Add fast preflight.
- Add regression tests.
- Update contract docs.

Before signoff:

- Prove no normal-path fallback usage.
- Prove all public surfaces agree.
- Prove migration bridges are blocked or explicitly tolerated.

## Field Semantics

Do not reuse names for different meanings. For example:

- `candidate_count` can mean discovered, deduped, profile-ready, board-visible, projection membership, or exportable.
- `ready` can mean data fetched, indexed, visible, reviewed, or terminal.
- `completed` can mean provider done, local materialization done, user-visible done, or post-processing done.

If meanings differ, use different names and owners.

