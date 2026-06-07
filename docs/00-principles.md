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

## 8. Work in Explicit Loops

AI-assisted engineering works best as a visible loop, not as a long hidden
implementation run:

1. Plan: define the decision, contract, artifact chain, boundaries, and gate.
2. Execute: implement the smallest coherent unit against the accepted contract.
3. Test: validate code and generated artifacts with fast fail-closed checks.
4. Analyze: compare outputs against the decision the phase is supposed to
   enable.
5. Review: ask an independent reviewer to judge the right gate with a packet.
6. Adopt: change defaults, schedules, publication, or user-facing claims only
   after the adoption gate passes.

Skipping early design usually moves discovery to the most expensive point:
late workflow tests, live runs, or manual review.

Use the loop to move discovery earlier. If an implementation repeatedly finds
basic issues only after live tests or manual smoke runs, stop and improve the
design artifacts, schemas, preflight checks, or review packet before continuing.

## 9. Design Artifacts Must Be Executable In Principle

A plan-only artifact is useful only if it can become a safe implementation
without changing its meaning. Before implementing a planner, adapter, report, or
runner, ask:

- What exact downstream decision should this artifact enable?
- Which later actions remain explicitly blocked?
- What schema, digest, boundary flags, and redaction rules make it auditable?
- What negative tests prove the artifact cannot be mistaken for stronger
  evidence?
- What real output will the artifact produce, and who will consume it?

If the answer is vague, keep the work in design. A script that produces
unreviewable or non-consumable output is usually technical debt, even when the
script itself works.

## 10. Missing Inputs And Tools Are Work Items

When an agent cannot read or validate required context because a dependency,
binary, account, browser, parser, OCR/PDF tool, or provider fixture is missing,
record the gap as a tracked work item. Include:

- what could not be read or verified;
- which capability was missing;
- whether the current conclusion is partial because of that gap;
- the recommended workspace-level dependency or setup change;
- whether user approval is needed before installing or using it.

Do not let missing-context gaps disappear in chat history. They should be
visible in TODOs, progress notes, or environment dependency docs before the next
phase treats the work as complete.

## 11. User-Invisible Fallback Must Stay Operator-Visible

A degraded or fallback response can be invisible to the end user, but its use must always
be visible to operators: logged, counted, and surfaced in metrics or preflight. This
reconciles "always return a graceful result" with "no hidden fallback" — the fallback is
graceful for the user and recorded for the operator. A fallback no one can see is a silent
normal path. See `11-safety-and-degradation.md`.

## 12. Model Output Is a Contract

When the system depends on a generative model, the prompt and the output shape are
production contracts. Version prompts, validate output against an explicit schema at the
boundary, and keep records so behavior can be reviewed, compared, and rolled back. See
`10-prompt-and-model-output-contracts.md`.
