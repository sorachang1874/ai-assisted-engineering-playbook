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

