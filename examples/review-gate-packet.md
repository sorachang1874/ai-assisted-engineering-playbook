# Example: Review Gate Packet

This example shows the shape of a review packet for a plan-only provider
collection planner. It is intentionally generic: the same pattern applies to
payments, search providers, enrichment APIs, export pipelines, data imports,
and background workflow runners.

## Gate

- Phase id: `p2-provider-collection`
- Gate type: Design Gate
- Requested verdict: `GO`
- Lifecycle step being reviewed: plan-only collection planner before any live
  provider execution.
- Previous gate evidence ref: `docs/reviews/review-gate-index.md#provider-policy-baseline`
- This gate must decide: whether the planner contract is complete enough to
  implement without enabling live provider calls.

## Objective And Non-Goals

- Objective: define a plan artifact that turns reviewed policy and candidate
  work items into an operator-reviewable execution plan.
- Non-goals: no live request, no secret value read, no cache write, no user
  claim, no publication, no scheduler.
- Decisions enabled if this gate passes: implement the plan-only artifact
  producer.
- Decisions still blocked if this gate passes: live execution, scheduled runs,
  user-visible output, and default configuration changes.

## Artifact Chain

| Stage | Artifact | Schema | Visibility | Producer | Consumer | Redaction | Overwrite Policy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Source | `policy_review.json` | `provider_policy_review.v0` | internal | policy reviewer | planner | no secrets | immutable review id |
| Source | `work_items.jsonl` | `work_item.v0` | internal | worklist builder | planner | opaque item ids | immutable run id |
| Plan | `collection_plan.json` | `provider_collection_plan.v0` | internal | planner | review, operator handoff | placeholders only | no overwrite |

## Boundary Flags

- External requests allowed: `false`
- Provider calls allowed: `false`
- Secret values may be read: `false`
- Cache writes allowed: `false`
- User-facing output allowed: `false`
- Publication allowed: `false`
- Scheduled or remote execution allowed: `false`

## Claims To Verify

1. The plan artifact is specific enough for implementation.
2. The command template uses placeholders only.
3. No boundary flag can be reinterpreted as live execution approval.

## Validation Package

```sh
make test-contract
make test-unit
```

## Review Outcome

Record the verdict in a tracked review index. Detailed transcripts can remain
local or private, but the durable project state should reference a redacted
summary.
