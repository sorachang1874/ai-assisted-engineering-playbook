# Runtime and Environment Isolation

## Required Modes

Define runtime modes explicitly:

- Local dev: fast, developer-owned, may use partial data.
- Scripted/fake-provider: deterministic, production-like dependencies, no paid external calls.
- Local live: targeted provider calls with strict budgets.
- CI contract: fast preflight and targeted integration.
- Nightly/pre-release: full long-chain signoff.
- Production: hosted service with durable state and audit logs.

Do not let mode be inferred from arbitrary environment variables. Use a central runtime config.

## Evidence Classes

Runtime mode should be reflected in the evidence you produce. A run can succeed
technically while still being the wrong evidence for a downstream claim.

Useful evidence classes include:

- plan-only: no execution, only preconditions and planned actions;
- local diagnostic: useful for debugging, not proof of production behavior;
- scripted/fake-provider: deterministic behavior with no external cost;
- clean local live: targeted live evidence under a known local environment;
- remote runner: evidence from a separate host or region;
- private/paid redacted: structurally useful but not redistributable;
- public-source static: safe to inspect but not necessarily quality evidence;
- external-provider: bounded live calls with budget, rate, and audit records;
- publication evidence: explicit proof that an artifact is safe to leave the
  workspace.

Record evidence class in generated artifacts and reports. Do not let local
diagnostic or remote-runner evidence silently promote production readiness,
user-facing claims, or publication.

## Data Isolation

Each mode should have isolated:

- Database/schema.
- Object storage prefix or bucket.
- Provider credentials.
- Cache namespace.
- Workflow run namespace.
- Export destination.

Production data should never be mixed with test data. If historical data is already mixed, create an explicit archive, exclusion manifest, and backfill plan.

## Storage Rules

For production-like durable runtime state, use the same storage class as production. Avoid maintaining SQLite or in-memory alternatives for normal workflow paths if production uses Postgres or another real database.

Use lightweight stores only for:

- Pure unit tests that do not validate runtime semantics.
- Migration compatibility tests.
- Local experiments that cannot be confused with service behavior.

## Testcontainers

Use containerized dependencies where behavior matters:

- Database semantics, locks, indexes, migrations.
- Object-store behavior.
- Provider fake HTTP servers.
- Browser smoke environments.

Avoid fixed ports, hardcoded hostnames, floating `latest` image tags, and shared mutable containers in CI.
