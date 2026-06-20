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

## 13. Match Measurement Effort to Evidence Value

Before building heavy execution scaffolding for a measurement, ask what its result is
worth and how stable it is. Evidence that varies by region, network, provider, or time
is low-value as a one-shot sample from a single vantage — a manual run captures one
unrepresentative point, and the gates, approvals, and runbooks around it can cost more
than the answer. Such measurements belong on scheduled, repeated collection from a
representative in-region vantage, not a one-off manual execution.

Practical consequences:

- Decide the execution model (one-shot manual vs scheduled multi-sample, and which
  vantage) from the evidence's variance and value, not from whichever path is easiest to
  authorize first. Designing the cheap path first can sink real review effort into an
  artifact that is then correctly shelved.
- It is a valid and common outcome to fully build and gate a capability, then defer
  executing it because the evidence is not worth the run. Record the deferral and the
  rationale; keep the reviewed design/code/schemas as reusable inputs for the right
  execution model later.
- When you defer or shelve an authorized action, revert any armed boundary
  (feature flag, permission, allowlist) to its closed state and mark the authorization
  withdrawn. An authorization left standing for a run that will not happen is exactly the
  hidden-open-boundary risk the rest of these principles work to prevent.

## 14. Independent Review Means a Different Model

A review gate whose reviewer is the same model that produced (and self-critiqued)
the artifact inherits that model's blind spots — it tends to confirm its own
reasoning. A genuinely *independent* gate uses a **different model family** as the
reviewer. In practice, cross-model review repeatedly surfaces real
false-negatives that same-model adversarial self-review does not: a fresh model
re-derives the problem from the artifact instead of from the author's framing, so
it catches misuse of an API, an unhandled edge case, or an over-claimed guarantee
the author's family systematically overlooks.

Practical consequences:

- Route the gate review to a model from a different family than the one that
  authored the work. Keep the author model's multi-lens adversarial self-critique
  as a *cheaper pre-gate pass* — it removes the obvious problems before the more
  valuable cross-model gate, but it is not a substitute for it.
- Treat agreement between two same-family reviewers as weaker evidence than one
  cross-family verdict. Diversity of failure modes, not redundancy, is what makes
  a review trustworthy (this is the review analogue of perspective-diverse
  verification).
- Operationalizing an external-model gate from inside a sandboxed agent has real
  friction: the agent's own execution sandbox may not have a network path to the
  external model's backend (egress allowlists, DNS interference). Be ready to run
  the cross-model gate from the human's host shell, or to establish a clean egress
  path, rather than assuming the agent can call it directly. For the validated
  invocation and the stdin/pipe/sandbox operational rules, see the Cross-Model
  Review Runbook in `07-multi-agent-parallel-work.md` (and the gate-process
  summary in `08-review-and-delivery-checklists.md` § Cross-Model Gate Review).
- The blind spot a cross-model gate most reliably catches is the **same-worktree
  blind spot**: an in-worktree reviewer — the author, or a sub-agent sharing the
  working tree — verifies against the files as they sit, not against what a clean
  checkout would see. It cannot notice tracked code importing an *untracked* local
  module, an oracle or test routed only to the new file while the real code still
  lives in the old one, or a symbol whose definition was never committed. A
  reviewer that re-derives from a fresh checkout finds these. Make "does this
  import and run from a clean checkout?" an explicit gate question rather than
  assuming a green working-tree run implies a green clean-checkout run.
- Once a class of change is *already* covered by independent adversarial
  sub-agent verification, the cross-model gate can run as a **non-blocking
  reference lane** instead of a blocking gate: fire it in the background
  (read-only, scope-pinned to a base commit) while the primary verification runs;
  proceed on the primary verdict; read and triage the cross-model result when it
  lands — real findings fixed forward in a follow-up, false positives recorded.
  Never roll back landed work solely because a *reference* review is still
  pending. Destructive or non-rebuildable-asset operations keep the blocking gate;
  the async lane never applies to them. This keeps the cross-model signal without
  serializing every change behind an external model's latency.

## 15. Fail-Closed Validators Are Allowlists, Not Denylists

When a checker must be *fail-closed* — reject every unsafe artifact, not just the
known-bad ones — do not build it by enumerating bad patterns. A denylist never
terminates against an adversarial reviewer: each round closes some patterns and
reveals subtler ones (nested forms, transitive graph paths, name shadowing,
substring-vs-token confusions), an effectively endless long tail. Instead assert
that the artifact **exactly matches a known-safe canonical shape** (an allowlist):
any deviation is rejected at once, closing whole classes of mutation rather than
one pattern at a time. Switching a stalled denylist checker to a canonical-equality
allowlist is usually the move that finally lets a fail-closed claim hold.

Practical consequences:

- Keep the canonical shape as a **single source of truth** that the generator
  emits and the validator deep-equals. When the same contract is realized in more
  than one language (e.g. a generator's in-language mirror plus an emitted script),
  add a **parity test** that runs the emitted artifact and compares it to the
  reference implementation, so the two cannot drift.
- An allowlist still has a structural long tail (duplicate names, cross-namespace
  collisions, unresolved graph references, first-match shadowing). Proving complete
  fail-closure approaches formal verification; an adversarial cross-model gate will
  keep sampling new exotic shapes. Decide in advance what the practical bar is —
  "substantive fail-closed properties independently verified, with the generated
  artifact provably canonical" is often enough — versus chasing an asymptote of
  ever-rarer inputs the generator never produces.
- Distinguish what the checker statically enforces from what is a runtime
  attestation. Some safety properties (a name's runtime selection, host-level
  behavior) cannot be settled by inspecting the artifact; label those as
  gated attestations rather than claiming the static checker covers them.

## 16. Attribute a Failure Before You Own It

A test that fails after your change is not yet evidence that your change broke it.
Before you debug, fix, or roll back, run the **control experiment**: put the code
back to the pinned pre-change baseline (`git stash` your diff, or check out the
base commit) and run the same failing test. If it fails identically there, the
failure is pre-existing and your change is innocent. Attributing it to yourself
wastes effort and can trigger a wrong "fix" that masks the real regression.

The control run is cheap — re-run only the failing tests, not the suite — and
decisive, and it is the discipline that keeps a refactor honest. A sub-agent
reviewer will confidently blame N suite failures on a structural change; a control
run pinned to the base commit routinely refutes most or all of them.

Practical consequences:

- Maintain a **known-failure budget**: a recorded list of failures already proven
  pre-existing by control attribution. A new entry requires the control run first
  — a failure is not "known" until it is attributed. The budget lets a
  green-modulo-budget run count as a pass without re-litigating each failure every
  batch, and the same set re-appearing unchanged after your edit is itself the
  proof you added nothing new.
- The same technique proves the *opposite* when you do change behavior: stash the
  fix and show the regression test fails on the baseline, then passes with the fix.
  That round-trip is what makes a regression test trustworthy rather than vacuous.
- Distinguish "my change *caused* this" from "my change *surfaced* this" — e.g. a
  test that only now runs because a guard began requiring a real dependency, or a
  test-isolation artifact that a schema change exposed. Both are
  control-attributable; the remedy differs.

## 17. Prefer Deletion to Wrapping; Classify Before You Sweep

When refactoring toward a single source of truth (principle 1), the first question
for each legacy path is not "how do I wrap or adapt this?" but "is it still
reachable at all?" A dual-code path whose branch is dead under the current contract
is removed, not rewritten: deleting it eliminates the divergence-bug class at the
root, and is *lower* risk than a rewrite because the deleted branch was already
never executing. "Reduce sources of truth" is served better by deletion than by
another compatibility layer.

For a large mechanical sweep — deleting the same dead branch across hundreds of
sites — do not trust the name or the count:

- **Classify each site before editing.** A predicate's call-count is not the
  edit-count: the same guard lives in read methods (safe to collapse) and in
  write/mirror methods (different shape, usually deferred). A method named like a
  reader can update-then-select. Scout and label every site — read vs write vs
  entangled — first.
- **Adversarially verify the classification; default to DEFER.** Have an
  independent pass try to *refute* that each site is safe to change; only sites
  that survive get edited. A scout map that is merely "probably right" will
  mis-edit the one write that looked like a read.
- **Preserve the exact observable behavior of the surviving path**, including its
  no-row / error sentinel (`None` vs `{}` vs `[]` vs `0` vs raise). Deleting dead
  code must be behavior-identical under the live contract — verify per batch, not
  once per sweep.
- Batch by cohesive group, verify each batch against its real consumers, and keep
  the entangled minority for a later structural pass rather than forcing it into
  the mechanical one.
