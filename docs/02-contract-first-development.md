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

## Artifact-First Phase Model

For non-trivial work, plan from the artifact chain backward:

1. Decision: what decision should be possible after this phase?
2. Evidence: what artifact legitimately supports that decision?
3. Contract: what schema, owner, producer, consumer, fallback, redaction, and
   overwrite policy govern the artifact?
4. Validation: what fast check proves the artifact is coherent?
5. Review: what gate must pass before the artifact can be used downstream?
6. Adoption: what separate gate is required before defaults, schedulers,
   publication, or user-facing claims change?

This prevents a common agent failure mode: implementing a useful-looking script
only to discover later that its output cannot be interpreted, reviewed, or
consumed safely.

## Schema And Storage Before Code

Define the schema and storage boundaries before writing a producer. For each
artifact, decide:

- schema version and required top-level fields;
- producer and downstream consumers;
- visibility: public, internal, local-only, private, or secret-bearing;
- redaction rules and sensitive-output scan scope;
- overwrite, append-only, and retention policy;
- freshness or TTL semantics;
- snapshot digest or reviewed-field drift checks;
- allowed write modes and the gate required for each mode.

Separate raw inputs, intermediate plans, execution records, reusable caches,
reviewed facts, human reports, and publication bundles. A local diagnostic
record should not share a path or schema with a durable reviewed fact. A sample
cache should not silently become a main cache.

When a provider or external system supports only single-item calls, design the
cache and append semantics before adding pseudo-bulk behavior. Deduplicate work
before requests, skip fresh cache rows, flush partial success safely, and record
interrupted runs as partial rather than rewriting history.

## Phase Registry

When work spans multiple turns, agents, or review gates, keep a small structured
phase registry near the code. The registry should record:

- phase id, title, lifecycle stage, and status;
- the decision the phase enables;
- non-decisions the phase must not be used for;
- effective-result criteria: proves, does not prove, required evidence, and
  downstream consumers;
- required design, implementation, and adoption gates;
- boundary flags for risky behavior such as external calls, secret reads,
  publication, scheduling, and user-facing output;
- the next artifact to produce.

See `templates/PHASE_REGISTRY.template.yaml` and
`examples/phase-registry.yaml`.

The registry is not bureaucracy. It gives agents a durable source of truth when
chat history is long, compacted, or missing. It also turns review-gate triggers
into something that fast preflight can validate.

## Field Semantics

Do not reuse names for different meanings. For example:

- `candidate_count` can mean discovered, deduped, profile-ready, board-visible, projection membership, or exportable.
- `ready` can mean data fetched, indexed, visible, reviewed, or terminal.
- `completed` can mean provider done, local materialization done, user-visible done, or post-processing done.

If meanings differ, use different names and owners.

## Snapshot Drift

A review approves a snapshot, not just a filename. If an implementation consumes
a reviewed policy, schema, command template, or provider configuration, record a
digest or reviewed-field snapshot and compare it before use.

Fail closed on drift:

- produce a blocked artifact or issue count;
- do not silently continue with the changed source;
- do not let long workflow tests be the first detector.

This applies to provider policies, prompt contracts, generated config,
publication manifests, migration plans, and any artifact whose meaning depends
on prior review.
