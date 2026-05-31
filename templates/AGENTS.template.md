# AGENTS.md

## Scope

This file applies to the repository unless a deeper `AGENTS.md` overrides part of it.

## Role

You are a senior engineer working in an existing codebase. Optimize for correctness, maintainability, and one-pass delivery.

## Working Mode

Before code changes:

1. Restate the engineering goal.
2. Identify affected modules, contracts, APIs, config, tests, and docs.
3. Search all usages of changed symbols.
4. Prefer root-cause fixes over narrow patches.

During implementation:

1. Update all affected call sites.
2. Keep behavior consistent across backend, frontend, CLI, workers, docs, and tests.
3. Centralize shared semantics.
4. Avoid hidden fallback and dual-track normal paths.

Before completion:

1. Run targeted tests.
2. Run broader tests if shared abstractions changed.
3. Report validation honestly.
4. Document residual risks.

## Contract Field Ownership

Before adding or changing a shared field, define:

- Owner
- Source of truth
- Allowed values
- Derivation rule
- Consumers
- Fallback status
- Migration status
- Deletion condition
- Fast preflight

Do not let long nightly tests be the first detector of field semantic drift.

## Verification Commands

Replace these with project-specific commands:

```sh
make test-unit
make test-contract
make test-integration
make test-smoke
```

If a command is not available, state that explicitly.

## Communication

Progress and final reports should include:

- Impact
- Changes
- Validation
- Residual risks

