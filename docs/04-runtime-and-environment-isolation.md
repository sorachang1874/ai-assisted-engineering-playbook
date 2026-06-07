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

## Workspace-Level Tooling

Some tools are shared across many projects but are too heavy, fragile, or
duplicative to install independently in every repository. Manage them at the
workspace level when they are:

- browser runtimes or browser system libraries;
- document/PDF/OCR extraction tools;
- container engines or remote-runner CLIs;
- network diagnostic tools;
- stable local command shims;
- large model, test, or data-processing runtimes.

Document the canonical workspace path, install source, version or checksum,
required system packages, validation command, and project entry points that use
the tool. Repositories should call the workspace tool through a stable shim or
documented command, not through ad-hoc absolute paths copied from another
project.

Before installing a new shared tool, check whether an equivalent already exists
in the workspace. Prefer one maintained dependency surface over many project
copies. If the tool changes execution behavior, evidence collection, remote
access, or generated outputs, route the change through a design or
implementation review gate.

## Missing Tool Follow-Up

If a run cannot inspect required materials because a parser, browser, library,
CLI, or system package is missing, do not treat the resulting analysis as
complete. Record:

- the blocked file, URL, fixture, or verification step;
- the missing capability;
- the temporary fallback, if any;
- the recommended dependency scope: project-local, workspace-level, container,
  or operator-provided export;
- the next command that should pass after installation.

Then ask for approval when installation has cost, security, credential, or
system-wide implications. This keeps "could not read the PDF" or "browser
runtime missing a system library" from becoming invisible lost context.
