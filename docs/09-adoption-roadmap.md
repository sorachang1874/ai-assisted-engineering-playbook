# Adoption Roadmap

## Day 0: Seed the Project

- Add `AGENTS.md`.
- Add `NEXT_TODO.md`.
- Add `PROGRESS.md`.
- Add basic test commands.
- Document runtime modes.

## Week 1: Make Contracts Visible

- Write contracts for core APIs and shared states.
- Add owner matrix for user-visible fields.
- Add first contract preflight.
- Start documenting migration bridges.

## Early Product: Stabilize Testing

- Separate local, scripted, live, and production data.
- Use production-like database in integration tests.
- Add fake provider server for workflow paths.
- Add browser smoke for critical flows.
- Keep live provider tests targeted and budgeted.

## Growth: Make Workflows Durable

- Introduce append-only events.
- Add typed commands/outbox.
- Add activity runs and attempts.
- Add current-state tables.
- Add read models and fail-closed readers.
- Remove normal-path legacy fallbacks.

## Mature Product: Make Agents Safe Operators

- Add OperationRun and AgentAction.
- Add action registry.
- Add approval gates.
- Expose retry/cancel/resume APIs.
- Expose provenance and entity deltas.
- Build UI/action queue only after backend semantics are stable.

## Continuous Improvement

After every incident:

- Write the root cause.
- Add a fast preflight if the bug was a contract issue.
- Remove one hidden fallback or heuristic if possible.
- Update the playbook if the lesson is reusable.

