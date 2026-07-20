# NEXT_TODO

This is a bounded project snapshot, not an append-only backlog or decision log.
Keep only current, blocked, and immediately next work. Link detailed work to
the owning module and replace stale rows during each refresh.

## Snapshot Metadata

| Field | Value |
| --- | --- |
| Owner |  |
| Last refreshed | YYYY-MM-DD |
| Next cleanup | YYYY-MM-DD |
| Size budget | 200 lines |
| Documentation router | `docs/README.md` |

## Current Objective

Describe the active engineering objective.

Canonical module route or work item: `docs/modules/<module>/README.md`

## Active Module Routes

| Module | Current/blocked/next item | Canonical detail | Owner | Status |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Phase Status

| Phase | Goal | Status | Evidence | Next Step |
| --- | --- | --- | --- | --- |
| P0 | Contract foundation | open |  |  |
| P1 | Implementation | open |  |  |
| P2 | Verification | open |  |  |
| P3 | Cleanup/deletion | open |  |  |

Status values:

- `open`
- `in_progress`
- `blocked`
- `done`
- `migration_only`

## Deletion Gates

Track old paths that must be removed.

| Old path | Replacement | Normal-path blocked? | Deletion condition | Owner |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Contract Questions

Questions that need product or architecture decisions.

| Question | Recommendation | Decision | Date |
| --- | --- | --- | --- |
|  |  |  |  |

## Missing Context Or Tooling

Track inputs, tools, dependencies, or credentials that prevented complete
inspection or validation. These items should not live only in chat history.

| Missing input/check | Missing capability | Current fallback | Impacted phase/artifact | Recommended follow-up | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Validation Matrix

| Gate | Command | Required Before | Last Result |
| --- | --- | --- | --- |
| Unit | `make test-unit` | PR |  |
| Contract | `make test-contract` | PR |  |
| Integration | `make test-integration` | merge |  |
| Nightly | `make test-nightly` | release |  |

## Snapshot Cleanup

- Remove completed rows after durable evidence is linked from the owning module.
- Move decisions to decision records and contract detail to contract docs.
- Move historical narrative to review/release artifacts only when it has durable
  value; otherwise delete it.
- Refresh at milestone boundaries and at least weekly during active work.
