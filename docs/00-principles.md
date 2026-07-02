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

## 29. Review Converges to an Asymptote — Give Every Gate a Termination Criterion

An independent review gate (principle 14) run repeatedly over the same artifact does not converge
to zero findings; it converges to an **asymptote of residuals**. Principle 15 drew this line for
fail-closed validators (generator-reachable findings versus hand-edit-only ones, with the threat
model written down before the gate opens); principle 18 drew it for the same-family self-critique
pre-pass; this principle generalizes the terminator to any gated artifact — including the case
where the residual is architectural, a trust-model fact, rather than threat-model-excluded. Once
the fixable classes are exhausted, every further round re-derives the same architectural residual
in new phrasing, because an LLM reviewer is rewarded for producing findings and has no natural way
to say "done." We learned this when a security gate reviewed its own installation change: nine
verdict rounds in a single day, of which rounds three through nine each re-discovered — in
different words — the one residual that had already been explicitly accepted (a reviewer sharing
the author's credentials can be self-signed), a fact no amount of re-review could change. An
unterminated gate either blocks indefinitely or gets habitually skimmed; both destroy the gate.

- **Classify each round's findings into three bins, with a declared adjudicator — and stop on the
  rule.** (a) A *new fixable class* — fix it with its siblings and ripple in one round
  (principle 19). (b) An *already-fixed class re-cited* — evidence about reviewer noise, not about
  the artifact; to earn this bin a finding must point to the specific commit or prior gate round
  that fixed the class. (c) A *residual that cannot be closed within the current trust or
  architecture model* — to earn this bin a finding must cite a residual-ledger entry id
  (principle 30). A finding that can point to neither defaults to (a) and blocks; the
  classification is confirmed by the lead or a human, never declared unilaterally by the author's
  agent. When a round produces only (b) and (c), stop iterating — past the asymptote, further
  rounds burn budget, add no information, and train the team to discount a gate whose tenth,
  genuinely novel finding then gets skimmed. These adjudication rules are checklist lines in
  `08-review-and-delivery-checklists.md` § Cross-Model Gate Review.
- **Make the terminator executable — the ledger diff is semantic, so force citation by id.**
  Residuals come back re-derived in new phrasing, so no text diff can match them; instead, the
  gate run feeds the full residual ledger (`templates/RESIDUAL_LEDGER.template.md`, principle 30)
  to the reviewer as input and requires every finding classed as residual to cite a ledger entry
  id. A round whose every finding cites a matching entry resolves as "no new information — pass
  with recorded residuals" instead of blocking; any finding that cites no entry still blocks.
  Termination is a stop rule, not a waiver.
- Pair this with principle 32: retro-validation decides when a gate *starts* blocking; the
  termination criterion decides when a given review *stops*. Both replace enthusiasm and fatigue
  with a pre-declared, measurable decision.

## 30. A Deliberate No Is a Ledger Entry With a Tripwire

A correct finding you deliberately do not fix does not disappear — and with memoryless reviewers it
does not even stay quiet. Fresh agent sessions, new audits, and every future gate round re-surface
the same true-but-accepted finding at full cost, and a human burns credibility re-explaining a
decision that was already made. The known-failure budget (principle 16) institutionalizes
acceptance for test failures; generalize it to every deliberate "no": accepted review residuals,
deferred or frozen features, automation declined, architectures rejected. Each becomes a **ledger
entry** — what was accepted, why, and what the correct fix would be — plus a **tripwire**: the
measurable condition under which the acceptance expires and the fix becomes mandatory. The ledger
is a checked-in, machine-checkable artifact — `templates/RESIDUAL_LEDGER.template.md` fixes the
columns: id, scope (which gate or artifact), what was accepted, why, the correct fix, the
tripwire, owner, date. Subsequent reviews then diff against the ledger instead of relitigating it.
This is principle 13's build-then-defer given an expiry — and per principle 13, any armed boundary
is reverted to its closed state while the tripwire waits.

- **Every deliberate no carries its own expiry.** An accepted security residual gets a trigger like
  "more than one semi-autonomous agent, or any external contributor" — the acceptance was scoped to
  a threat model, so its expiry is that model's boundary. This is principle 1's deletion condition
  applied to decisions instead of code.
- **Defers and freezes need both a light-up and a kill condition, written into the tracking item.**
  "Frozen" without conditions is unstable: maintenance leaks in, the freeze drifts back to keep,
  and the same audit has to re-run from scratch months later. A written pair ("re-activate when X;
  delete if nobody has used it 30 days past its window") turns each defer into a self-executing
  future decision instead of a recurring debate — and gives the next audit a diffable baseline.
- **Grow automation by pre-committed tripwires, and keep a ratified never-do list in the same
  ledger.** Machinery is nearly free for agents to build and never free to own; decide in advance
  what evidence justifies the next tier ("LLM triage only after three real misroutes"; "a hard CI
  gate only after the advisory digest is ignored twice"), and record with equal weight what you
  will *never* build and why — otherwise every new agent re-proposes the rejected architecture,
  forever. Never-do items are ledger entries with status `never` plus ratified-by and date fields,
  and `08-review-and-delivery-checklists.md` requires any new-mechanism proposal to diff against
  the never-do entries before it is argued on the merits.
- **Calibrate the conditions themselves.** Tripwires can be drawn wrong; attach a metric that says
  so (e.g. "if post-hoc human vetoes of the advisory tier exceed 20%, the tier boundary is wrong").
- **An entry without a tripwire is prose (principle 28)** — unbounded acceptance is forgetting with
  a paper trail. The fixed-column format makes this lintable: tripwire is a required column, and a
  minimal preflight lint (an entry missing its tripwire exits nonzero) runs with the other fast
  checks (principle 3).

## 31. A Gate Must Guard Its Own Control Plane — and Safety Tooling Gets No Wrap-Up Sweeps

The files that implement a gate — detector code, policy document, setup scripts, verdict parser —
are the highest-leverage attack and decay surface in the repository: a change that edits them can
weaken the gate without touching any path the gate protects, and routine maintenance ("just
tooling", "just docs") walks through that hole innocently. A cross-model review caught exactly
this class: a gate-installation change whose mechanical protected-path list omitted the gate's own
detector script, sweep tool, and policy document — all three modified by the very change under
review, and each able to weaken or obscure the gate.

- **Enumerate the gate's own files inside its own protected set**, and prove it with a synthetic
  test: a change touching only the detector must trip the gate. A gate that does not guard itself
  gets silently disarmed by maintenance long before any attacker tries.
- **Declare one side the source of truth between detector code and policy prose**, and check the
  other against it — otherwise the two drift and the prose becomes a lie about what is enforced.
  This is principle 21's derived-copy problem, playing out between code and documentation.
- **No confidence-driven touch-ups to safety tooling at wrap-up.** The riskiest edits are the
  untested "while I'm at it" hardenings made while closing out a task — precisely the code whose
  failure modes are platform-specific and unexercised by local checks. In one gate's history, a
  commit fixed a BSD `mktemp` trap (a template suffix after the `X`s is taken literally, so the
  "random" temp name isn't random at all); the very next commit — a wrap-up "tighten temp-file
  permissions" security sweep — reintroduced the identical bug. Hardening commits get feature-grade
  test discipline: if you cannot test the edit here, do not make it here. This is diff hygiene
  (principle 24) applied to the one class of file where a harmless-looking improvement can disarm
  a gate. (Both this pitfall and the self-protection gap above are rows in the Pitfall Log of
  `13-operator-decisions-and-evidence-integrity.md`.)
- **Fail-closed construction is the last line, and it will be needed.** The reintroduced bug's
  damage was bounded only because the gate cannot pass what it cannot parse: no machine-readable
  verdict means do-not-merge. This extends principle 20 to the recursive case — when the component
  *is* the enforcement, there is no outer mechanism to hard-depend on, so fail-closed construction
  is all that survives an agent editing the gate under time pressure.
- **The verdict a gate emits is itself a model-output contract (principle 12), applied
  recursively** — SHA-bound, machine-markered, anchored-parse, injection-fenced,
  identity-restricted, fixture-tested; a verdict accepted by regex anywhere in any comment is
  forgeable by accident, by stale copy-paste, and by prompt injection. The full mechanics, the
  minimal marker spec, and the must-reject fixtures live in
  `10-prompt-and-model-output-contracts.md` § Review Verdicts Are Model Outputs Too, with a
  conforming example in `examples/cross-review-verdict-example.md`.

## 32. A Gate Earns Veto Power on Ground Truth — Retro-Validate Before It Blocks

New review gates get adopted on faith, and faith resolves in one of two bad ways: the gate blocks
without proven value and gets resented, or it emits noise and gets ignored. Before a new gate is
allowed to block anything, **falsify it**: run it retroactively against artifacts that already
passed your best existing process — merged, human-reviewed changes — and check that it yields real,
non-trivial findings rather than silence or noise. This is principle 16's control experiment
pointed at the reviewer instead of the test suite: known-good history is the baseline, and the
gate's signal is measured against it *before* the gate acquires power.

- **Pre-declare the decision rule before the run, in copyable form.** The rule that worked:
  retro-run the gate against the two or more most recent merged, human-reviewed changes; at least
  one finding the author confirms would have required a code change ⇒ the gate earns its blocking
  posture; zero such findings ⇒ it ships advisory-only, with a re-evaluation scheduled (90 days or
  a fixed number of runs). "Author-confirmed, code-change-requiring" is the operational line
  between real and trivial, and declaring both branches in advance is what stops the result from
  being argued into whatever the author wanted.
- **The retro-run is the gate's acceptance test, and it is nearly free**: no live traffic, no
  waiting for the next incident — the history already exists. When we retro-ran a new merge gate
  over two already-merged, human-reviewed changes, it surfaced real defects in both (a save path
  that bypassed a freshly built fallback; a read-before-write idempotency race; an undocumented
  change to shared semantics) — so its blocking authority was activated on evidence, not
  enthusiasm.
- **Attach the transcript to the installation change.** The gate's authority should be auditable by
  anyone who later wants to revoke or extend it; "it found these real defects in code our best
  process had already passed" is the durable answer to "why does this thing get to block me?" The
  transcript lives in the installation PR's description or under `examples/`, and the review
  packet's gate section carries a retro-validation evidence reference
  (`templates/REVIEW_PACKET.template.md`).
- Pair with principle 29: retro-validation decides when a gate starts blocking; the termination
  criterion decides when a given review stops — both are pre-declared checklist lines in
  `08-review-and-delivery-checklists.md` § Cross-Model Gate Review, which also fixes where the
  gate sits in the delivery flow.

## 33. Review Machinery Manufactures Work for Itself — Someone Must Keep the Total-Cost Ledger

Ask a multi-lens audit — or any standing reviewer — to judge a product surface and it structurally
outputs "keep everything, improve everything": every lens sees some value, no lens is charged with
the total cost of ownership, and LLM reviewers amplify the bias because they are rewarded for
findings and findings are almost always additive. A six-lens audit of forty-four features produced
zero deletions and fifteen-plus new tickets; only a deliberately opposed adversarial pass — a
deletion advocate chartered against a protect-the-core advocate — converted that into two real cuts
and eleven defers and freezes. Treat "0 cuts, +N tickets" as a red flag about the audit itself, not
as a fact about the product.

- **Name the accountant.** One explicit role — a human or an adversarially-chartered critic — sums
  the maintenance tax across all the keeps and is rewarded for deletions and freezes. Executable
  form: `templates/AUDIT_SYNTHESIS.template.md` requires a cuts-and-freezes count, a summed
  cost-of-ownership line, the reversal log, and the cut-critic's sign-off; its built-in self-check
  question — zero cuts plus net-new tickets without the cut-critic's explicit concurrence — fails
  the audit's own acceptance.
- **Run opposed charters and record the verdict reversals.** Let two critics with opposite mandates
  attack the same synthesis; write outcomes as explicit reversals with the losing argument
  preserved (the reversal log is a required section of the same synthesis template), and label
  unresolved disagreements with a recommendation. The reversal log is the audit's highest-value
  output — it is what makes the audit auditable by the human who has to decide. This is
  independence of *objective*: the incentive-side complement of principle 14's independence of
  model family.
- Pair with principle 34: the same audit that manufactures keep-everything output is also where the
  untracked queue of human rulings surfaces — audit for that queue deliberately, because no lens is
  chartered to see it either.

## 34. The Bottleneck Is a Queue of Human Rulings — Decisions Are Work Items

Once agents accelerate implementation, throughput is often governed not by engineering but by
human sign-off latency on zero-engineering decisions: product boundaries, quota values, policy
scope. Because decisions are not "work items", no engineering board shows them on the critical
path — so audit for them deliberately. The audit of principle 33 found effort flowing to polish
for unconfirmed future features while a weeks-old queue of yes/no decisions gated fifteen-plus
engineering tasks and two work lanes — and three actively-bleeding defects (signed URLs already
expiring in production, a public deployment with no spend gate, zero database backups) sat
unstaffed. This extends principle 10 from missing tools to missing **rulings**: a pending human
decision is a missing input, and missing inputs are tracked work items.

- **Make the decision queue a first-class artifact** — an owner, a deadline per item, and a visible
  landing place (a `decisions/` directory or a fixed section of the project status board) that the
  next audit can diff; schedule a decision session rather than letting the queue drain by chance.
- **Pre-build a decision card for every queued ruling** so the human spends minutes per decision,
  not days. Required fields (`templates/DECISION_CARD.template.md`): the single question to be
  answered, the options with the evidence for each, a recommendation, the deadline, the default
  that fires on timeout, and who decides.
- **A ruling that automation will consume gets the stricter regime** — hand-authored decision
  files with value and generation binding, machine-validated per batch; see
  `13-operator-decisions-and-evidence-integrity.md`. The queue and its cards govern getting the
  decision *made*; that document governs what the decision must look like once machines depend
  on it.

## 35. A Fleet With a Hard Single-Model Dependency Fails as a Fleet — Declare Per-Lane Fallback

Any fleet with a hard single-model dependency fails *as a fleet*: when a ten-agent audit fan-out
hit model-quota exhaustion mid-run with no fallback declared, nine of ten agents died and the
batch produced nothing. It did not degrade — it zeroed. A degraded batch is reviewable and
salvageable; a zeroed batch is a rerun. So every routed lane pre-declares a designated alternate,
and quota exhaustion triggers automatic per-agent fallback instead of a dead stop.

- **The routing table is a checked-in artifact (principle 22).**
  `templates/MODEL_ROUTING.template.yaml` holds one row per lane, each naming its primary model,
  its designated fallback, and its constraints — including a review lane's prohibition on falling
  back to the author's family, and the declared behavior on quota exhaustion (degrade versus
  explicit defer). Routing decided in chat at dispatch time gets re-decided — differently — by
  every future dispatcher. The dispatch checklist in `07-multi-agent-parallel-work.md` asserts
  three things before fan-out: the table exists, every lane names a fallback, and no review route
  resolves to the author family.
- **Record every fallback in the handoff** so quality drift stays operator-visible — the handoff
  artifact carries a *model used / fallback fired?* field. A silent model downgrade is a hidden
  fallback (principle 2): the work looks done, but the workhorse quietly did the reasoning lane's
  job. Same rule as every degraded path — invisible to the flow, visible to the operator
  (principle 11).
- **The independence lane is a constraint, not a preference.** The fallback for a cross-model
  review lane must never resolve to the author's model family — defer the gate visibly (and let the
  residual ledger of principle 30 record the skip) rather than silently substitute the author's
  family and call the result independent review.
- **The specific task-nature assignments are project policy, not principle.** Routing
  reasoning-dense work (planning, research, review, audit) to the deepest reasoner and
  execution-dense work (writing code and tests, mechanical migration) to the high-throughput
  workhorse is the current table's content — date the assignments and revisit them as models
  change. What this principle fixes is only that the table exists, is checked in, and carries a
  fallback clause for every lane.

## 36. Autonomy Is Delegated Up a Ladder — Verification First, the Prompt Last, and Every Rung Declares a Stop Condition

An agent's loops differ by what the human still supplies — interactive, goal-driven, scheduled, event-driven — and those four form a ladder of what gets handed over: first the verification steps, then the stop condition, then the trigger, and only last the prompt itself (one vendor's 2026 loop guide names exactly these four rungs; full citation in `docs/references.md`). Climbing a rung is legitimate only once the rung below can be verified without you — trust is demonstrated verification capability, never granted upfront. One team climbed exactly this ladder for its coordination control plane — a manual sweep, then a deterministic sweep script, then an event-driven triage bot — and pre-declared in its control policy the metric that unlocks each next rung ("LLM triage only after three real misroutes"), so every escalation of autonomy was a recorded decision instead of drift.

- **Hand over in the fixed order: verification, stop condition, trigger, prompt.** Skipping ahead — automating the trigger while the output is still verified by vibes — is how loops end up running unwatched with nobody able to state what "correct" looks like. The rung you are on is defined by the last thing you still do yourself.
- **Every loop declares a stop condition and an attempt cap before it runs.** A loop without a declared exit runs until token exhaustion or silent drift. Goal loops need a verifiable completion criterion plus a max-attempts cap ("Lighthouse ≥ 90 or stop after five tries"); deterministic criteria — tests pass, queue empty, PR merged — outrank "the model judges it good enough". Principle 29 owns the review-round case; this clause owns every other loop: retry loops, generate-and-polish loops, self-iteration with no reviewer.
- **Scheduled rungs match the interval to the watched object's real change rate — and prefer events to time.** Polling faster than the world changes burns budget re-observing an unchanged world; where the platform offers events (webhooks, CI triggers, issue hooks), replace the poll entirely — as one team found when it retired a 20-minute polling cron for event-driven triage, which also survived the death of the local session that used to run the poll.
- **A rung upgrade is a tripwire row, not a mood.** Pre-declare the measurable threshold that unlocks the next level of automation, and when it fires, record the grant as a dated row — what was handed over, the evidence that unlocked it. This is principle 30's tripwire machinery pointed at a yes instead of a no, and the delegation twin of principle 32's rule that a gate earns its veto on ground truth.
- **Executable form:** the brief's existing `## Stop Conditions` section (`templates/AGENT_TASK_BRIEF.template.md`) gains three lintable lines — stop criterion (deterministic where one exists), attempt/budget cap, trigger (`event` or `interval` plus justification); the dispatch preflight (doc 07) fails any brief that launches a loop with those lines empty; and doc 14's board row gains an `expected-done` column — the predicted completion time doc 14's sweep checks a running loop against — a field this change introduces to the row schema.

## 37. A Top-Tier Model Is a Consultant or a Planner Before It Is the Whole Task — and Tier Access Itself Is a Lease

Principle 35 keeps a fleet alive when a quota wall hits by declaring per-lane fallback; this principle governs the layer before any fallback fires: how a single task composes model tiers, and the fact that top-tier access is usually quota-bound, promotional, or revocable — a lease, not a property. Two compositions come with vendor-reported numbers — Anthropic measuring its own models on its own benchmarks, not replicated here; treat them under principle 16's control-experiment discipline, exactly like the STOP claim in doc 16 (Anthropic advisor/orchestrator guidance; claude-cookbooks `managed_agents/CMA_plan_big_execute_small.ipynb`, 2026): **advisor** — a cheap model executes and consults the expensive model only at decision junctures, reported at ~92% of the expensive model's solo SWE-bench Pro score at ~63% of its cost, often on a single consult per task; **orchestrator** — the expensive model plans, splits, and synthesizes while cheap workers do all token-heavy reading and writing in parallel contexts, ~96% of solo performance on BrowseComp at ~46% of cost ($1.61 vs $4.00, 194s vs 608s, at an identical verification standard). What those numbers support is not "never solo" but a shifted default: the top-tier model rarely needs to run the whole task — solo is the composition that now carries the burden of proof.

- **Choose the composition by task shape — and give the choice one home.** Execution-heavy with rare hard forks → advisor; planning- and synthesis-heavy over bulk I/O → orchestrator; and solo stays legitimate where the last points of accuracy are the product — an accuracy-critical lane may keep the top tier end-to-end, recorded as a deliberate choice in the routing table's comments, not left as an unexamined default. The routing table's per-lane `composition:` is the lane default; a brief may override it per task, and the override is recorded in the handoff — one ruling, one wording, so no dispatcher has to guess which of two homes wins.
- **Model asymmetry is not role asymmetry.** The lead/worker dispatch pattern (doc 07) splits roles and ownership; advisor/orchestrator splits model tiers. They compose — a lead can be an orchestrator — but conflating them hides the cost decision inside the org chart.
- **Junctures are declared, consults are logged.** The advisor economics come from rarity — declare in the brief where the executor may escalate, and record each consult in the handoff. Zero consults on a task whose brief declared junctures is a Deviations check (doc 15); zero consults on a fork-free task is the advisor economics working, not drift. An executor that always consults is paying two models to do one job.
- **Tier access is a lease — principle 26 at the model boundary, calendar half only.** Principle 35 already owns the quota dimension — per-lane degrade targets, `on_quota_exhaustion`, and the handoff annotation of every fired fallback; the lease adds the calendar dimension principle 35 does not cover: a promotional window closes on a date, so it carries an expiry, a renewal owner, and a per-stage pay-to-renew decision. A quota wall discovered mid-run kills the run (the incident behind principle 35); a declared calendar expiry merely downgrades it — declare the expiry before depending on the tier.
- **Executable form:** `templates/MODEL_ROUTING.template.yaml` gains a top-level `models:` section — one entry per model, lanes reference models by name — whose `lease:` block carries exactly three fields: `expires` (a date, or `none` for self-hosted or owned models), `renewal_owner`, `on_calendar_expiry`; quota behavior keeps its single existing home, the per-lane `on_quota_exhaustion`. Each lane gains a `composition:` field (`solo | advisor | orchestrator`, `solo` with a justifying comment). The dispatch preflight fails a route only when a model's lease block is missing or its `expires` date has passed — `expires: none` is legal — exactly as it already fails a lane without a declared fallback (principle 35).

## 38. The Evaluator Lives Outside the Loop It Judges — Accept a Mechanism Change Only on Held-In Plus Held-Out Evidence

Principle 31 stops a gate's own files from being edited by the work the gate reviews. This principle defends against the attack that needs no file edit at all: optimization pressure. A loop that improves against a signal will fit the signal — overfit the tests, game the judge model, exploit benchmark gaps (Lilian Weng, "AI Harness", lilianweng.github.io/posts/2026-07-04-harness/, 2026-07-04) — so the evaluation criteria, the scoring rubric, the judge, and the permission layer must sit outside both the loop's modifiable range and its optimizable range. The one-line boundary: "the author cannot edit the gate's files" is principle 31; "the loop cannot optimize against the evaluator's observable signal" is this one.

- **Out of reach in two senses — only one of them new here.** Un-editable is principle 31's territory — detector, rubric files, and config in the gate's own protection set, verdicts SHA-bound to the exact artifact version per `10-prompt-and-model-output-contracts.md` § Review Verdicts Are Model Outputs Too — and family diversity is principle 14's. What this principle adds is un-fittable: acceptance includes a held-out signal the loop cannot observe while it iterates; the scoring rubric's details are not disclosed to the loop being scored; and any change to the evaluator or its permission layer routes through the highest gate — the control-policy tier no agent may approve on the human owner's behalf — never through the loop it constrains.
- **A mechanism change passes a double gate: held-in and held-out.** Accept a change to the harness only when a held-in check confirms the targeted weakness is actually fixed AND a held-out check confirms nothing else broke (Self-Harness, via Weng 2026-07-04). "The targeted test now passes" is half an acceptance criterion — it admits placebo fixes and regressions the fix smuggles in. A per-fix test paired with an end-to-end smoke on fakes is the everyday shape of the same gate.
- **Never remove the only regression guard before its successor exists.** Deleting or replacing a guard is itself a mechanism change and passes the same double gate — as one team's feature audit ruled, the artifact carrying the sole end-to-end guard could not be deleted until a successor smoke was in place.
- **A rejected candidate is evidence, not garbage — but recording it is principle 39's machinery.** The harness loop consumes that record: a new proposal is diffed against the negative-evidence log before it spends a run.
- **Executable form:** `08-review-and-delivery-checklists.md` § Cross-Model Gate Review gains the line "does this change touch a signal some loop optimizes against? — then that loop's own outputs are inadmissible as the change's evidence"; harness-change PRs carry held-in and held-out evidence fields; a guard deletion with no named successor guard fails review.

## 39. A Negative Result Is Evidence With an Expiry Date — Record the Mechanism, Not the Symptom

Principle 30 owns deliberate noes — rulings, with tripwires; principle 16 owns failures you attribute before owning; doc 13's Pitfall Log owns the pits that already bit someone. None of them owns the layer beneath: the attempt that simply failed — the prototype that dead-ended, the model a bake-off excluded, the fix that didn't fix. Models are trained on success-skewed data and under-report failure (Weng 2026-07-04), so unless saving a failed attempt is the path of least resistance, the evidence evaporates and the next agent re-runs the experiment blind. And a negative result decays: it is a fact about a version at a date, not about a name — one team seeded a model-selection survey with version numbers from old notes and anchored the whole survey on superseded models, missing two newer releases until the founder caught it.

- **Record the mechanism at three depths, never the symptom.** Direct cause, causal state, abstract mechanism (Weng 2026-07-04): two runs with identical error logs can have entirely different root causes, and a symptom-level record misroutes the next fix.
- **Every record is dated and version-bound — and therefore expires.** "X can't do Y" is true of X-at-version-v-on-date-d, not of the name X; reading a negative record past its subject's next major release is a prompt to re-run the experiment, not a license to obey the old verdict. Stale negative evidence is worse than none — it silently excludes the option that has since become the right one.
- **Make saving the failed attempt the path of least resistance.** The pipeline cannot depend on the model's candor about its own failures: the handoff carries a required negative-evidence field — `none` is written explicitly, a blank fails the dispatch preflight.
- **The log is load-bearing, not archival.** Principle 38's harness loop diffs each new proposal against it before spending a run; and a failure that hardens into a decision never to retry graduates into principle 30's ledger with a tripwire — this principle owns the raw evidence beneath those rulings.
- **Executable form:** `templates/NEGATIVE_EVIDENCE.template.md`, instantiated beside the project's residual ledger — one dated row per abandoned attempt: what was tried · model/version/date · direct cause · causal state · abstract mechanism · why abandoned; the handoff template's negative-evidence field is required (`none` allowed, blank not); `08-review-and-delivery-checklists.md`'s harness-change review diffs proposals against this file.

## 40. A Gate Round May Overturn a Prior Round — Primary Sources Beat Precedent

A multi-round review gate is evidence-driven, not precedent-driven. The failure mode: round 1
suggests a fix, the author complies, and every later round treats the round-1 framing as settled
— so a *wrong premise* gets hardened into code, tests, and comments with each round "confirming"
the previous one. Rounds must stay free to refute earlier rounds, including the reviewer's own
prior suggestion, when a primary source (upstream source code, the spec, the vendor's parser)
says otherwise. Correctness beats consistency with the transcript.

- **When a fix encodes a semantic claim about an external system** (an init system, a kernel
  interface, a browser, a wire protocol), the review scope must include *verifying that claim
  against the primary source*, not just checking the code implements the claim faithfully. A
  fix can be internally perfect and semantically wrong.
- **Reward the reversal, don't litigate it.** A real case: round 1 proposed modeling "an empty
  assignment resets the dependency list" (true for most of that config format's list settings);
  the author complied, with a red-team fixture demonstrating the "reset bypass". Round 2 — the
  same reviewer — refuted its own round-1 premise by citing the upstream parser: *dependency*
  directives are accumulate-only and an empty assignment is a no-op, so the "bypass" did not
  exist and the checker's rejection message explained something false. The reversal was the
  most valuable finding of the gate; accepting it cost one round, entrenching it would have
  cost every future reader.
- **Mechanically:** prompt each confirming round with the prior round's verdict *attached* and
  an explicit license to overturn it with sources; never scope a round to "confirm the fixes"
  so narrowly that refuting the fix's premise is out of bounds.

## 41. Separate Semantic Modeling from Policy — Lint Your Preferences Explicitly

When a validator encodes rules about an external system, keep two layers visibly distinct:
**semantics** — what the system actually does, modeled faithfully with the primary source cited
— and **policy** — what you *additionally* refuse even though the system would accept it.
Collapsing policy into the semantic model produces validators that reject with false
explanations ("this resets your dependency" when it doesn't), red-team fixtures that document
nonexistent attack vectors, and future readers who learn wrong semantics from your code.

- **The semantic layer is not yours to design.** Its only correctness criterion is fidelity to
  the external system; cite the source (spec section, upstream function) in the docstring so
  the next reader can re-verify rather than re-derive.
- **The policy layer is yours — so say so.** Reject the suspicious-but-harmless shape (an
  ineffective reset attempt, a no-op directive with no legitimate use) with a message that says
  *policy*, names the shape, and says why it is suspicious — not a message that misattributes a
  behavior to the external system.
- **Fixtures follow the split.** A must-reject fixture for a policy lint asserts the lint
  message, and its comment says "no-op in the real system, rejected as policy"; a fixture that
  claims to demonstrate a real bypass must actually be one. A fixture with a false premise is
  negative documentation — it teaches the attack that isn't.
- Being stricter than the external system is fine (fail-closed, principle 20); *describing* the
  external system wrongly is not. The test: could someone learn the external system's real
  behavior from your checker's messages and comments alone? If not, the layers are merged.
