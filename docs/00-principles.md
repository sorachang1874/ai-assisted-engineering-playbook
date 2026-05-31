# Engineering Principles

## 1. Contracts Before Implementations

If a field, state, API, file, or event affects user-visible behavior or workflow recovery, it is a production contract. Define the contract before relying on it.

Every contract needs:

- Owner
- Source of truth
- Allowed values
- Derivation rule
- Consumers
- Fallback behavior
- Migration bridge status
- Deletion condition
- Fast preflight

If a field is not in an owner matrix, it is not ready for normal-path use.

## 2. No Hidden Fallback

Fallbacks are useful during migration, but dangerous when they become invisible normal paths. A fallback must be:

- Report-visible in metrics or preflight output.
- Blocked by normal-path signoff unless explicitly tolerated.
- Documented with a deletion condition.
- Covered by a migration-only test, not normal-path tests.

## 3. Short Feedback Before Long Feedback

Long pressure tests, nightly runs, and live validation should prove stability, latency, and recovery. They should not discover basic contract drift.

Before long tests, run fast checks for:

- Cross-endpoint field parity.
- Owner/source-of-truth consistency.
- Schema and command registry completeness.
- Fallback or migration bridge usage.
- Provider fake contract compliance.

## 4. Separate Intent, Execution, and Read Models

Keep these layers distinct:

- Intent: user or agent wants something.
- Command: system has accepted an action to perform.
- Activity: bounded side effect such as a provider call or file write.
- Event: append-only record of what happened.
- Current state: materialized operational state.
- Read model: optimized user-facing projection.

Do not let UI readers repair state. Do not let workers independently decide cross-stage lifecycle transitions.

## 5. Design for Agent Operation

An AI agent should operate the system through explicit surfaces:

- OperationRun or equivalent intent record.
- Action registry.
- Approval gate.
- Typed command registry.
- Activity status and retry/cancel/resume API.
- Read-only provenance and metrics APIs.

Agents should not mutate domain tables directly.

## 6. Environment Separation Is Product Infrastructure

Local development, scripted/fake-provider testing, live provider validation, staging, and production must be different modes with clear data boundaries. Shared mutable test databases and "almost production" scripts create drift.

## 7. Documentation Is Part of Delivery

Docs are not optional if behavior changes. Update:

- `AGENTS.md` when agent behavior or workflow changes.
- `NEXT_TODO.md` when phase status changes.
- `PROGRESS.md` when a handoff matters.
- Contract docs when fields, events, commands, APIs, or owners change.
- Signoff docs when test gates or runtime modes change.

## 8. User-Invisible Fallback Must Stay Operator-Visible

A degraded or fallback response can be invisible to the end user, but its use must always
be visible to operators: logged, counted, and surfaced in metrics or preflight. This
reconciles "always return a graceful result" with "no hidden fallback" — the fallback is
graceful for the user and recorded for the operator. A fallback no one can see is a silent
normal path. See `11-safety-and-degradation.md`.

## 9. Model Output Is a Contract

When the system depends on a generative model, the prompt and the output shape are
production contracts. Version prompts, validate output against an explicit schema at the
boundary, and keep records so behavior can be reviewed, compared, and rolled back. See
`10-prompt-and-model-output-contracts.md`.

