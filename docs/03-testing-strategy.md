# Testing Strategy

## Testing Pyramid for Agentic Projects

Use multiple layers instead of one expensive all-purpose test:

- Unit tests: pure logic, reducers, validators, parsers.
- Contract preflights: schema, owner matrix, cross-endpoint parity, command registry.
- Integration tests: real database, fake providers, object store, queues.
- Browser smoke: core user flows against local backend.
- Scripted workflow tests: realistic end-to-end workflows with provider fakes.
- Live provider validation: small targeted samples only.
- Nightly/pre-release: long-chain stability, recovery, latency, and pressure.

## What Long Tests Should Not Do

Nightly tests should not discover:

- A field has two owners.
- A reader still uses a legacy fallback.
- A command type has no owner.
- Two endpoints expose different contract semantics.
- A fake provider response shape differs from live expectations.

Those belong in fast preflight.

## Production-Parity Harness

For workflow-heavy systems, build toward:

- Real database type used in production.
- Real object-store behavior or a compatible stub.
- Fake HTTP providers that implement webhook, poll, dataset download, retry, rate limit, and error semantics.
- Browser runner for end-to-end UI smoke.
- Clean data per run.
- No shared mutable test state.

## Provider Testing

Provider tests should separate:

- Request construction.
- Remote submission.
- Poll/fetch.
- Item-level retry.
- Late result quarantine.
- Evidence/adjudication.
- Materialization.

Batch providers should expose stable item IDs, not rely only on array order.

## Pre-Manual Tests

Before manual QA, run a pre-manual gate that checks:

- Core endpoints are coherent.
- Readiness and counts use one source of truth.
- No normal-path fallback was used.
- Recent workflow metrics are within known ranges.
- UI does not expose contract/debug wording to end users.
- Provider fakes match live response shape for the tested path.

