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
- **Classify each late gate finding as generator-reachable or hand-edit-only — that
  test, not the reviewer's appetite, is what sets the stopping bar.** Once the
  generated artifact is deep-equal-locked to the canonical, every further finding is
  one of two kinds: a shape the generator *can actually emit* (a real defect — fix it
  and keep going), or a shape only a *hand-edit or exotic external input* could produce
  (the asymptote the bullet above names). If hand-edited artifacts are **not in your
  threat model** — the generator is the sole writer and its output is canonical-locked —
  the second kind is *out of scope*: record it as a known residual with its
  threat-model rationale and stop, rather than spending another serial gate round
  (principle 19) hardening the checker against an input that cannot reach production.
  The trap is that a cross-model gate keeps surfacing *genuine* false-negatives of the
  second kind — they are real bugs in the *checker*, so stopping feels like leaving
  defects unfixed — but each one defends a config your threat model already excludes.
  Write the threat model and the bar down **before** opening the gate, so a
  "real-but-unreachable" finding reads as a stop signal, not as another round. (A gate
  that ran ~11 rounds to clean, most of the tail closing exotic hand-edit shapes the
  generator never emits, is the symptom this prevents — and the fix is not better
  batching but an explicit scope decision up front.)
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

## 18. Audit Against the Source of Truth Before the Gate

The findings a cross-model gate (principle 14) most reliably contributes — and the
ones a same-family adversarial self-critique most reliably *misses* — are
**doc-grounded**: a misused API semantic, an unhandled default, a negation or
wildcard spelling, a precedence rule. Same-family critique reasons from the
artifact's own framing and the author model's *recollection* of how the upstream
tool behaves; it inherits the author's mental model, so it cannot catch a place
where that model is simply wrong about the tool. Worse than missing them, it can
*confirm* a wrong model in the artifact's favour — "verifying" a guard that the
upstream tool's real semantics make unnecessary or incorrect (e.g. a validator that
rejects a config value the tool actually *requires*). Both the imagined hazard and
its "fix" are then wrong, and no number of further same-family rounds will surface
it because they all share the same false premise.

So before spending a cross-model round-trip, **be the doc-grounded reviewer
yourself**: enumerate every upstream surface the artifact depends on and verify each
against the *actual reference doc*, not from memory or from re-reading the code.

- **Enumerate the surfaces.** For anything that inspects or emits an external
  contract — a config schema, CLI flags, a unit/rule file, a wire format — list the
  fields, directives, and value forms it touches, and open the upstream doc for each.
- **Check the four classic gaps,** which is where doc-grounded findings cluster:
  *defaults* (an absent field is not automatically the safe value — know what the
  tool defaults to), *negation / wildcard / set spellings* (`!= x`, `{a,b}`, `+.x`,
  inverted sets — the unsafe form often dodges a check written for the positive
  spelling), *precedence / last-assignment* (a later line can silently reset an
  earlier safe one), and *required vs forbidden* (a value your validator rejects may
  be one the tool mandates — confirm direction against the doc).
- **Prefer the canonical-shape allowlist (principle 15) so the audit is finite.**
  When the validator asserts an exact known-good shape, the source-of-truth audit is
  "does the canonical shape match the upstream schema?" — one question — instead of
  "have I enumerated every unsafe deviation?", which the docs will always extend.
- **Know the stopping bar, and where the next finding lives.** A same-family
  adversarial pre-pass converges fast on same-family blind spots and then chases an
  asymptote; the *next* real class will not come from another self-critique round —
  it comes from the docs. Cap the self-critique (one or two multi-lens rounds), run
  the source-of-truth audit, *then* open the cross-model gate. This converts a
  series of gate round-trips — each surfacing one doc-grounded class — into a single
  self-audit pass plus a confirming gate.

## 19. Minimize Gate Round-Trips, Not Findings Per Round

A cross-model gate round-trip (principle 14) is expensive and **serial**: minutes of
reviewer latency, a fresh artifact bundle, and round N+1 cannot start until round N's
verdict lands. So the cost of a gate is dominated by the *number of rounds*, not the
number of findings in any one. The discipline is to make each round retire as much as
possible — and the anti-pattern is the slow convergence where each round fixes exactly
the one line the reviewer cited and re-gates.

- **Front-load discovery across every surface the gate will audit.** Principle 18 says
  audit upstream semantics before the gate; generalize it: the pre-gate self-review must
  cover *every* surface the gate inspects, not just the mechanical validator. A
  fail-closed checker gets adversarially hardened, but the operator runbook's *sequencing*
  (does step 3 overwrite the file step 5 backs up?), the renderer's *side-effects* (perms,
  atomicity, stale-file cleanup), and the *documentation's* consistency (inventories,
  counts, cross-references) are surfaces too — and they are where the late, avoidable
  rounds get spent. Run these as parallel self-review lenses (principle 7) — secret-leak,
  ordering, side-effect/atomicity, fail-closed completeness, reversibility,
  doc-consistency — and drive self-findings to zero before opening the gate. Parallel
  local lenses are cheap; serial gate rounds are not.
- **Treat each finding as the representative of a class, and fix the class plus its
  ripple in one round.** Before re-gating, fix (a) every *sibling*: all the other paths
  with the same property — every early-return that skips the cleanup, every artifact with
  the same perms gap, not just the cited one; (b) the *ripple* of any change to a
  canonical/emitted shape — adding, splitting, or renaming an artifact or token opens a
  new surface the gate audits next round, so sweep it now (stale-artifact removal, perms,
  doc inventories and summaries, counts, validation coverage, cross-references); and (c)
  the *adjacent class* — if the gate flagged "validate the ports," also validate the CIDR,
  the identifiers, and the empty/null case in the same pass, before it asks.
- **Batch the long tail.** Once a gate reaches "no blockers, a handful of minor findings,"
  stop fixing one per round. Make a single consolidated pass that closes every open
  finding and the classes you can anticipate, then run one confirming gate. A full
  round-trip to confirm two cosmetic fixes is a bad trade — fold them into the pass that
  earns the approval.

The failure mode this prevents is real and recurring: an atomic-publish requirement fixed
across three separate rounds — introduce the cleanup, then learn it runs on only one
failure path, then learn an early return skips it entirely — when a single "enumerate
every path that must clean up, and what each leaves behind" pass in the first round would
have closed it. The reviewer's job is to *confirm* the class is closed, not to *enumerate*
its members for you one round at a time.

## 20. Couple a Component to Its Safety Enforcement — Fail Closed When It's Absent

When a component's safety depends on a *separate* enforcement mechanism — a firewall/allowlist,
a network policy, an auth proxy, a sidecar — the dangerous failure mode is not the component
crashing; it is the component running **normally while unprotected** because the enforcement is
missing or failed to load. That fails *open*. Make the component **hard-depend** on its
enforcement: it must refuse to start (or to serve) unless the enforcement is provably in effect.

- Express the dependency where the runtime enforces it: a `Requires=`/`After=` (or equivalent)
  on the enforcement, **plus a pre-start assertion that the enforcement is actually in effect** —
  assert the specific firewall *chain/rule* (or policy) exists, not merely that the enforcement
  *service* started. A started-but-empty enforcement is the gap a unit-level dependency alone
  misses.
- Write the check that proves the *negative*: with the enforcement removed, does the component
  stay down / refuse to expose itself? Verify it (remove the enforcement, confirm no exposure);
  don't assume it.
- This is the deployment-time twin of the fail-closed validator (principle 15): a validator
  fails closed on bad *input*; a service must fail closed on absent *enforcement*. Both replace
  "assume safe" with "prove safe, or don't run."
- A cross-model gate (principle 14) reliably catches this class, because the author — focused on
  the happy path where the enforcement is present — systematically skips "what if the listener
  is up but the firewall isn't?" A real near-miss it caught: a SOCKS5 landing whose daemon would
  have started and exposed a residential exit IP to the whole internet had its firewall failed to
  load; the fix bound the daemon to the allowlist chain's presence (`Requires=` + an
  `ExecStartPre` asserting the chain), so a missing firewall keeps the daemon down instead.

## 21. Validated Is Not Delivered — Verify at the Surface the Consumer Reads

When one authored source fans out into several generated artifacts, the trap is editing — or
validating — the *wrong copy*. A change can pass every test, checker, and pin and still never
reach production, because the artifact your validation reads is a **different derived copy** than
the one the consumer reads. "Validated" is not "delivered." Before treating any file as a source,
prove it isn't a derivative; after any change, verify it at the *delivery* surface, not the
validation surface; and make the source→derived propagation one command with a drift guard so no
copy silently rots.

- **Prove provenance before editing a file as a source.** Regenerate it to a scratch location and
  diff against the committed one. If it reproduces, it's a *derivative* — editing it directly is
  clobbered on the next regen, or worse, silently desyncs the copies the regen doesn't touch. The
  real source is whatever the generator *reads*, not whatever looks hand-written. A "single source
  of truth" refactor (principle 17) starts here: map the generation DAG before you move a line.
- **Verify at the delivery surface.** Tests and checkers often read an intermediate artifact (a
  merge file, a bundle); the consumer reads a different one (the rendered profile, the deployed
  config). Grep the change in the artifact the consumer *actually* loads. A green suite on the
  wrong copy is *validated-but-not-deliverable* — the most expensive false pass, because it looks
  done. The real near-miss: a domain added to the merge file the checker reads passed 700+ tests
  and the pin went up, but the operator's rendered profile — generated from a *separate* extension
  file — never gained the domain; the "fix" shipped nothing.
- **One command, with a drift guard.** Make propagation source→every derived copy→every pinned
  constant a single command, and add a `--check` that regenerates to a snapshot and fails on any
  diff (ignoring only provenance timestamps). Staleness must be *detectable*, not silent: a
  renamed constant once sat stale in one generated copy indefinitely while the source and every
  other copy had moved on, because nothing regenerated-and-compared. This is the fail-closed
  validator (principle 15) applied to generated artifacts.
- **"Single source of truth" rarely means one file.** It means one authored input with a
  deterministic, guarded path to every copy. Flattening structured sources into one list just to
  have "one file" can destroy semantics (match-type, grouping) the generator needs; the
  higher-value fix is the one-command-plus-guard, not fewer files. Order the regen by dependency
  (regenerate a pinned constant *before* the artifact that self-checks against it, or the
  self-check fails mid-run).

## 22. Live Coordination Is Ephemeral; the Durable Truth Is Git

When several long-lived agents work one repo concurrently (separate processes, no shared memory —
see `14-async-multi-agent-collaboration.md`), they need a fast live channel for task claims,
heartbeats, questions, and decisions-in-flight. Keep that channel **local and gitignored** — it
removes every git race for co-located agents. But hold a hard line about what it *is*: the live
channel is a **bus, not a memory**. A decision that lives only there is invisible to every agent
that wasn't watching at that moment, and to every future instance, clone, and session.

- **Promote, don't leave.** When a live decision becomes normative — a frozen contract, a ratified
  principle, an ownership change — the author promotes the normative form to **git** (the contract
  file, a `docs/` doc, `AGENTS.md`) and only *announces* it in the live channel. When the two
  disagree, an agent trusts git.
- **One durable project-status snapshot in git** is the "where is the whole project" doc every agent
  reads at the start of every work chunk. Make "read it first" a standing rule in `AGENTS.md`, not a
  per-prompt reminder — so a fresh instance self-orients without a human re-explaining.
- This is the multi-agent twin of principle 21: there, a change "validated" on a derived copy never
  reached the consumer; here, a decision "agreed" on the live channel never reaches the next agent.
  Both fail because the artifact that was edited is not the one that gets read. Verify at the surface
  that is actually read — and for cross-agent, cross-session memory, that surface is git.

## 23. Merged Is Not Landed — Verify Integration by Content

A PR shown as "merged" is not proof that a branch's work is in `main`. Squash-merge collapses a PR's
commits into one against the PR's base *at merge time*; if the branch kept advancing, or a lower PR in
a stack merged early, later commits can sit in **no open PR and not in main** — silently stranded, and
easily masked because a running demo still serves from the local branch. `git --merged` ancestry is
unreliable across squashes and will confirm the wrong thing.

- **Verify by content, not by ancestry or by the squash message.** Grep `origin/main` for a marker you
  know belongs to the work in question; that, not "the PR says merged," is what tells you the cutoff.
- **Stop pushing to a merged branch.** Continued work goes on a fresh PR; pushing onto an
  already-squashed branch is how work strands.
- **After any peer's PR merges, rebase your branch on main before continuing** — long-lived parallel
  branches drift from a stale base, and the drift surfaces as phantom conflicts or lost work later.
- This is principle 21 ("validated is not delivered") at the merge boundary: the most expensive false
  pass is the one that *looks* done. Confirm landed work at the delivery surface — the merged content in
  `main` — not at the surface that merely *reports* success.

## 24. Separate Diff Hygiene From Refactor Appetite

Two different disciplines get conflated under "make small changes," and an agent needs them calibrated
**separately** — because one is universal and the other is a per-project decision. Conflating them makes
an agent either churn a stable codebase gratuitously or refuse a redesign an early-stage one needs.

**Diff hygiene is universal — it holds at every maturity level.** Every changed line should trace to the
task or to a *deliberately named* refactor; nothing else moves.

- **Match the file you're editing** — its quote style, casing, indentation, import idiom. File-internal
  consistency beats personal preference, and beats the model's training-data default. This is the same
  failure the "write code that reads like the surrounding code" rule prevents: an LLM pattern-matches to
  its training distribution and emits locally-plausible code that is globally inconsistent with the file.
- **Never reformat code you didn't have to change** — no whole-file formatter run on a non-formatted
  file, no taste-driven import reordering, no indentation churn. Reformatting buries the real change under
  noise and makes review and `git blame` painful.
- **No opportunistic orthogonal edits.** Fixing X does not license renaming a variable in Y or fixing a
  typo in Z. Clean up only the mess your change *caused* (an import you just orphaned), not pre-existing
  dead code someone else left.

**Refactor appetite, by contrast, scales with codebase maturity — it is a project decision, not a
universal rule.** The widely-circulated "minimal surgical diff, avoid early abstraction, repetition is
cheaper than the wrong abstraction" advice is calibrated for a *stable* codebase where the architecture
is settled and the dominant risk is gratuitous churn. An *early-stage product in active design* is the
opposite regime: under-abstraction calcifies into duplicated, divergent logic, and restructuring a wrong
early design is cheaper now than after it spreads. Do not import the stable-codebase defaults into an
early one, or vice versa — name the regime, then pick.

What makes aggressive refactoring *safe* in either regime is not avoiding it but **bounding** it:

- A refactor is **named, scoped, and its own change/PR** — never silent scope-creep smuggled inside an
  unrelated task. (That is the diff-hygiene rule above, enforced at the unit of work.)
- If it touches shared semantics it is a **contract change first** (principle 1): owner, consumers,
  deletion-condition — so an abstraction has a *named consumer and a removal path*, not a speculative
  "maybe later" with nobody on the other end.
- The deletion-over-wrapping and classify-before-sweep disciplines (principle 17) govern the refactor
  itself.

**The synthesis:** bold, deliberate refactoring — yes, as named bounded work; unintended, opportunistic,
style-churning diff noise — no. Early abstraction toward an *articulated* reuse — yes, under contract
discipline; speculative abstraction for an imagined future — no. Calibrate the first clause of each pair
to the codebase's maturity; the second clause holds always.

## 25. Snapshot Gates Cannot See Trajectory Defects — Contract the Verb, Not Just the Noun

A schema-validation + typecheck + review + CI pipeline verifies a VALUE's shape at a single instant, on
one invocation, on the happy path. A whole defect class lives in the complement: behavior at **t+Δ** (a
stored reference that was valid at write time and dead at read time), on **invocation #2** (what a
repeated action does), on the **error branch** (what renders when a dereference fails), and in the
**human viewport** (whether feedback was perceivable, not merely present in the DOM). These are
*trajectory* properties — properties of behavior over time and repetition — and no point-in-time gate can
reject them unless the contract regime reifies them as declared, enforced clauses. A real five-bug
incident from first live user testing decomposed to exactly this: every component was locally correct and
every gate was green; the missing facts were "this URL dies in ten minutes", "a second tap double-saves",
and "on 404 this tile goes permanently blank".

- **Contract user-facing actions as verbs, not just data as nouns.** A data contract answers "what is
  this value?"; a verb contract answers: what does a *repeat* invocation do (idempotency — enforced at
  the server choke point, e.g. a uniqueness key, not a client-side flag alone, because a network retry is
  also a repeat)? through what *surface* does the user learn it succeeded (acknowledgment)? what do the
  user and the operator each see on *failure* (the user-invisible/operator-visible split of principle 11)?
- **The actor model is part of the spec, and an unwritten one silently defaults to the developer's own
  behavior**: acts exactly once, perceives all feedback (which they placed, on their own screen), consumes
  results seconds after producing them, never revisits. Real users repeat when unsure, miss feedback,
  return after arbitrary delays, and get interrupted mid-flow. Tests derived from the spec inherit the
  same idealized actor — so "the second click is a no-op" was never a falsifiable claim anywhere in the
  system. Missed feedback and non-idempotent actions compound: the user who can't tell it worked is the
  user who clicks again.
- **The bar for each verb clause is an executable form — a failing test or a rejected write, never a
  sentence in a template.** "Idempotent to repeat, unmissable to confirm, durable to revisit": each
  adjective needs teeth — a double-fire test asserting exactly one effect; one blessed prominent-feedback
  component as the only allowed confirmation surface (ad-hoc variants linted out), since perceivability
  itself is not machine-checkable; and the lease rules of principle 26 for anything revisited later.
- Trajectory properties are exactly the ones a fake-driven CI is structurally blind to; principle 27 is
  how they are made testable at all.

## 26. A Borrowed Reference Is a Lease

Every value crossing a process or trust boundary is either **owned data** (self-contained, valid
indefinitely) or a **borrowed reference** — a URL, token, session, handle, or cache key that points into
someone else's resource and carries an issuer lease (a TTL, stated or not). The receiver always has a
holding period: a render loop, component state, a database row, an email. The defect class is
**retention > lease**, and it escapes every standard gate for three structural reasons: (1) the type
system erases lifetime — a ten-minute URL and a permanent URL are both `string`, so review literally
cannot see that `store(url)` is a bug; (2) the two timelines never meet in one artifact — the issuer's
TTL lives in a vendor doc, the retention decision in a different module written weeks later, so each half
passes review alone; (3) **every gate completes inside the lease window** — typecheck, unit, smoke, and
demos run in seconds-to-minutes while leases run minutes-to-days, so a defect that needs wall-clock time
greater than the pipeline's duration is invisible to every process that runs faster than the TTL.

- **The rule:** a reference whose lifetime you do not control must never be written into storage or
  long-lived state you do control. At the boundary, prove retention ≤ lease or convert:
  **materialize** (copy the bytes into owned storage), **re-mint** (store the durable ID and sign a fresh
  reference at read time), or **refresh** (hold the renewal credential, not the lease).
- **Enforce by construction at one choke point, not by declaration**: a single mandated converter (e.g. a
  write-through media proxy) plus a fail-closed write-boundary guard — the persistence layer rejects
  reference patterns matching known ephemeral issuers (reuse the proxy's host allowlist as the source of
  truth). Construction is robust to *unknown* TTLs, which is the defining feature of the class: the
  incident happened because nobody knew the lease existed, and no template field can force unknown
  knowledge.
- Give reference-typed contract fields a closed lifetime vocabulary — `durable | request-scoped |
  leased(ttl, expiry-strategy = materialize|re-mint|refresh)` — as a design-time prompt; but the teeth
  live in the guard and the hostile fake (principle 27), not in the doc row.
- Distinguish from ordinary cache staleness: a stale copy of *owned* data degrades (a wrong-ish value);
  an expired *borrowed* reference hard-fails (no value at all). Different failure mode, different fix —
  materialize/re-mint, not invalidate.
- The class is everywhere: a checkout-session URL emailed for "complete your purchase later" (404s in
  24h); an OAuth access token persisted where the refresh token belonged (everyone logged out at t+1h);
  S3/COS presigned URLs saved into database columns or CDN configs (every avatar breaks in 7 days); DNS
  answers cached past their TTL.

## 27. Fakes Must Match Production's Hostility, Not Just Its Shape

A test double is an implicit theory of which properties of the real dependency matter. CI's reward
function — deterministic, fast, always-valid — is the pointwise negation of reality's hostile properties
— outputs decay, responses lag, events arrive twice, calls fail mid-sequence. So kind fakes are
*systematic drift, not carelessness*: hostility causes "flaky tests" and gets engineered out, and the
suite ends up green not because the code handles reality but because the simulated reality contains no
hazard to handle. Shape parity ("fake matches live response shape") is the checkable half; the
**envelope** — how long outputs stay valid, how late they arrive, how often they repeat — lives outside
any schema, and the defects it hides are exactly principle 25's trajectory class.

- **Hostile by default**: fakes issue references that expire (after first dereference, or a count/virtual-
  clock TTL — never wall-clock sleeps), deliver one duplicate of every event, fail a scheduled call in the
  sequence. The escape hatch is an explicit KIND flag for debugging — never the reverse, because opt-in
  hostility never gets turned on.
- **Deterministic, never sampled**: scheduled hostility (every event delivered twice; call #3 fails), not
  random 1-in-K — a random hostile leg becomes the flaky test that gets tolerated and softened, recreating
  the kindness one level up.
- **A hostile fake is inert without a scenario that makes it bite.** The smoke needs a *revisit leg* —
  expire all leases at a session boundary, then re-read every persisted and displayed reference and assert
  zero blank/broken surfaces — and a *repeat leg* — double-fire each mutating action the smoke already
  exercises and assert exactly one effect. A fake that expires URLs nobody re-dereferences fails nothing.
- **Keep the hostility-dimension list closed and append-only** (expiry, duplication, latency/timeout,
  partial failure, ordering). Every production incident traced to a kind fake adds its dimension — the
  class-level analogue of a regression test (principle 16). Waivers ("concurrency: waived — single
  writer") carry an owner and a reason and are audited by the independent reviewer (principle 14), never
  self-attested by the fake's author.
- The economics that make this non-optional: fast CI *structurally* never lets a TTL elapse or a session
  grow old. Hostile fakes exist to compress time until the trajectory fits inside a thirty-second run.

## 28. A Norm Exists Only If a Machine Can Fail Because of It

Human teams paper over spec gaps with scar tissue — a senior engineer "obviously" debounces the save
button, "obviously" stores the bytes rather than the link. AI implementers build exactly the set of
properties some executable artifact asserts, and reproduce the spec's gaps with perfect fidelity; prose
norms bind whoever currently holds them in working memory, which across agent sessions is nobody. This
playbook is its own case study: "freshness or TTL semantics", "failure and retry semantics", and an
idempotency-key column all already existed here — as unenforced checklist prose — and a five-bug incident
shipped straight through them. Prose that no machine checks is documentation of intent, not a constraint.

- **The enforcement hierarchy, strongest first:** *by construction* (a choke point, a branded type, a
  structural default that makes the wrong thing inexpressible) → *CI gate* (a test or lint that goes red)
  → *template field* (a forced question) → *prose* (a hope). Push every norm as far up the hierarchy as it
  will go; a norm stuck at prose should be treated as not implemented.
- **Template fields are the weakest active form and decay fastest with AI implementers**: agents fill
  templates frictionlessly but not truthfully — a mandatory `reference-lifetime:` row gets a boilerplate
  "permanent" that passes the presence check while being wrong. Declarations also cannot capture *unknown*
  hostile properties; construction (a write boundary that rejects non-durable references regardless of
  what anyone declared) is robust to ignorance.
- **Some properties no machine can check** — whether feedback is genuinely perceivable, whether copy is
  age-appropriate. Do not pretend a gate covers them: give them a structural default (one blessed
  component as the only allowed surface, ad-hoc variants linted out) plus an explicit manual-signoff line.
  The honest gap is a named manual check; the dishonest one is a green suite that never asserted the
  property.
- **Corollary for postmortems:** the deliverable of a "lesson learned" is not the lesson's text but its
  executable form — the test that now fails, the guard that now rejects, the fake that is now hostile, the
  dimension appended to the hostility list. If the postmortem ends with prose, the class will recur.
