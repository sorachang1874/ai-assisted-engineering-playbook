# Example: Agent Task Brief

## Goal

Make export generation a durable typed command owner instead of a direct API-side file write.

## Non-Goals

- Do not redesign export UI.
- Do not change export field policy.
- Do not add new provider calls.

## Context

Read:

- `docs/EXPORT_CONTRACT.md`
- `docs/DURABLE_EXECUTION_RUNTIME_CONTRACT.md`
- `AGENTS.md`

## Required Changes

- Add `export.generate` command type.
- Add `export_owner` registry entry.
- API should plan command only.
- Owner writes export artifact and event.
- Read API exposes command state and artifact readiness.
- Add preflight that blocks direct normal-path export writes.

## Validation

Run:

```sh
make test-contract
make test-export
```

## Handoff

Report changed files, tests run, command owner behavior, and remaining migration bridges.

