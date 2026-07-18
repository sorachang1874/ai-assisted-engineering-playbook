# AI-Assisted Engineering Playbook

This repository captures reusable engineering practices for teams that use AI coding agents such as Codex, Claude Code, and similar tools. It is distilled from production refactoring experience in a workflow-heavy application where hidden fallbacks, ambiguous contracts, environment drift, and long-running verification loops created repeated regressions.

The goal is not to prescribe one stack. The goal is to make any stack easier for humans and agents to operate: clear contracts, isolated environments, layered tests, durable plans, explicit owners, and review habits that prevent expensive failures before nightly or live testing.

## Who This Is For

- Solo founders and early teams that want to avoid rewrites caused by weak early contracts.
- Growing teams that need AI agents to work safely across a larger codebase.
- Mature projects introducing multi-agent development, contract preflights, durable workflow runtimes, or production-like test harnesses.
- Teams using Codex, Claude Code, Claude Code subagents, GitHub agents, or custom agent orchestration.

## Core Principles

- Contract-first development: shared fields, states, APIs, and files need explicit owners, source of truth, consumers, fallback policy, and deletion conditions.
- No hidden dual tracks: migration bridges must be visible, blocked in normal-path signoff, and tracked to deletion.
- Fast preflight before long tests: nightly and pressure tests should validate stability and throughput, not discover basic semantic drift.
- Production-like test isolation early: use real dependencies where behavior matters, isolated data, fake providers, and separate local/scripted/live/prod modes.
- Durable execution for long workflows: append-only event log, typed commands/outbox, activity attempts, idempotency, leases, retry policy, and materialized current state.
- Agent-safe surfaces: agents should operate through operation/action/command APIs, not mutate domain tables directly.
- Documentation is runtime infrastructure: route problems through a project
  index into module-owned contracts, product artifacts, tests, and runbooks;
  keep root `NEXT_TODO.md` and `PROGRESS.md` as bounded snapshots rather than
  unbounded stores.
- Optimize the delivery graph, not agent utilization: freeze shared decisions,
  dispatch only dependency-ready lanes with disjoint writes, model review as an
  edge to promotion, and continuously distill failures and avoidable work into
  executable improvements.
- Reviews need packets, not just prompts: design, implementation, and adoption reviews should receive explicit artifacts, boundaries, evidence classes, validation output, and claims to verify.
- Plan-only artifacts before risky execution: external calls, cache writes, scheduled jobs, and publication should be preceded by reviewable plans that keep execution flags false.
- Schema and storage before code: define artifact shape, visibility, write mode, retention, redaction, and downstream consumers before building producers.
- Independent review gates are scoped: a `GO` approves only the named design, implementation, or adoption decision, not later live execution or public claims.
- Workspace-level tooling should be managed deliberately: shared browsers, parsers, CLIs, container runtimes, and document tools need stable shims, validation commands, and ownership.
- Missing context is a tracked work item: unread files, missing parsers, unavailable browser libraries, or skipped validation must be recorded before a phase is treated as complete.
- Model output is a contract: version prompts, validate output against a schema at the boundary, and keep records for review and rollback.
- Operator decisions are artifacts: human overrides, exceptions, and approvals live in hand-authorable decision files that are independently reviewed per batch and machine-verified (verdict, digest, item-decision pairing) before anything applies them.
- Derived artifacts carry digests of their inputs, and consumers verify all of them: partial digest checks create silent staleness, and status-string agreement is not freshness.
- New evidence consumers degrade or maintain existing interpretations, never promote them: score and status promotion is always its own gated change, and every status enum value needs both a producer path and a consumer branch.
- User-invisible fallback stays operator-visible: a graceful fallback for the user must still be logged, counted, and surfaced so it never becomes a silent normal path.
- Secrets stay server-side and out of commits and logs; runtime mode comes from one central config, not scattered env vars.
- Independent review means a different model: route the gate to a different model family than the one that authored and self-critiqued the artifact; same-model self-review shares blind spots, and cross-model review repeatedly catches false-negatives it misses.
- Fail-closed validators are allowlists, not denylists: assert the artifact exactly matches a canonical safe shape (single source of truth, emitted by the generator and deep-equaled by the checker, with a cross-language parity test) instead of enumerating bad patterns, which never terminates.
- Attribute a failure before you own it: re-run a post-change test failure on the pinned baseline (in a parallel worktree, not by flipping the shared working tree) before debugging — identical failure means pre-existing, recorded in a known-failure budget, not a regression you introduced.
- Prefer deletion to wrapping, and classify before you sweep: remove a dead dual path instead of rewriting it; for a large mechanical sweep, scout and adversarially verify each site (read vs write) before editing, preserving the surviving path's exact no-row/error sentinel.
- Minimize gate round-trips, not findings per round: a cross-model gate round is serial and high-latency, so front-load discovery with parallel self-review lenses over every surface the gate audits, fix each finding's whole class and the ripple of any canonical change in one round, and batch the long tail into a single confirming gate instead of a round-trip per cited line.
- Couple a component to its safety enforcement (fail closed when absent): a component whose safety depends on a separate enforcement (firewall/allowlist, network policy, sidecar) must hard-depend on it and refuse to start/serve unless the enforcement is provably in effect — assert the specific rule/chain exists, not just that the enforcement service started — so a missing enforcement fails closed (component down), not open (component running unprotected).
- Validated is not delivered — verify at the surface the consumer reads: when one source fans out into several generated artifacts, prove a file is the source (regenerate-and-diff) before editing it, verify a change in the artifact the consumer *actually* loads (not the intermediate the test/checker reads), and make propagation one command plus a regenerate-and-diff drift guard so no derived copy silently rots.
- Live coordination is ephemeral; the durable truth is git: when long-lived agents share a repo, keep the live channel (task claims, heartbeats, questions) local and gitignored, but promote every normative decision (frozen contract, ratified principle, ownership change) into git — a decision left only in the live channel is invisible to the next agent, instance, and session.
- Merged is not landed — verify integration by content: a PR shown as "merged" can leave later or stacked commits stranded in no open PR and not in `main` (squash collapses to the base at merge time, and `git --merged` ancestry misleads across squashes); confirm the cutoff by grepping `origin/main` for known content markers, stop pushing to a merged branch, and rebase on main after any peer merges.
- Separate diff hygiene from refactor appetite: diff hygiene is universal (match the file's style, never reformat untouched code, no opportunistic orthogonal edits — every changed line traces to the task or a named refactor); refactor appetite scales with codebase maturity (a stable codebase favors minimal-diff conservatism, an early-stage one welcomes bold redesign and early abstraction toward an articulated reuse), and what makes aggressive refactoring safe is bounding it — named, scoped, own-PR, contract-first — not avoiding it.
- Snapshot gates cannot see trajectory defects — contract the verb, not just the noun: schema/typecheck/review/CI all verify a value's shape at one instant on one happy-path invocation, while a whole defect class lives at t+Δ, on invocation #2, on the error branch, and in the human viewport; contract every user-facing action's repeat behavior, acknowledgment surface, and failure render, with each clause as a failing test or rejected write — never a template sentence.
- A borrowed reference is a lease: every URL/token/session/handle crossing a boundary carries an issuer TTL and every holder has a retention period; retention > lease is a whole defect class that hides because types erase lifetime, the two timelines never meet in one artifact, and every gate finishes inside the lease window — so never persist a reference whose lifetime you don't control: materialize, re-mint, or refresh at one constructed choke point with a fail-closed write-boundary guard.
- Fakes must match production's hostility, not just its shape: CI's reward function (deterministic/fast/always-valid) is the pointwise negation of reality's hostility (decay/delay/duplication), so kind fakes are systematic drift; make fakes hostile by default with deterministic scheduling, pair them with a revisit leg (re-read all persisted state after expiring leases) and a repeat leg (double-fire mutations, assert one effect), and keep an append-only hostility-dimension list fed by every incident.
- A norm exists only if a machine can fail because of it: AI implementers reproduce spec gaps with perfect fidelity and prose binds nobody across sessions; push every norm up the enforcement hierarchy — construction > CI gate > template field > prose — treat prose-only norms as not implemented, give machine-uncheckable properties a structural default plus a named manual check, and close every postmortem with an executable artifact, not a lesson's text.
- A standing review gate needs a termination criterion: classify each round's findings into three bins — a new fixable class (fix with its siblings in one round), an already-fixed class re-cited (must point to the fixing commit or gate round), or a residual unfixable under the current trust model (must cite a residual-ledger entry id) — stop when a round yields only the latter two, and make the terminator executable by feeding the ledger to every round: a finding that cites no ledger entry blocks, an all-matched round passes with recorded residuals — an unterminated gate blocks forever or teaches the team to skim it, and both destroy the gate.
- A deliberate no is a ledger entry with a tripwire: findings you accept, features you freeze, and automation you decline don't disappear for memoryless agents — record in a machine-lintable ledger what was accepted, why, and the correct fix, plus the measurable condition that expires the acceptance (light-up and kill conditions for defers, build-on-trigger thresholds and a ratified never-do list for machinery), so reviews diff against the ledger instead of relitigating, and an entry missing its required tripwire column fails the ledger's own preflight lint.
- A gate must guard its own control plane: a change editing the detector, policy doc, or setup scripts can weaken a gate without touching any protected path, so the gate's own files belong in its protected set (code declared source of truth over prose); never make untested wrap-up "hardening" sweeps to safety tooling, build gates fail-closed (no parsable verdict means do-not-merge) as the last line for when that rule is broken anyway, and treat the emitted verdict as a model-output contract — SHA-bound, machine-markered, anchored-parse, injection-fenced.
- A gate earns veto power on ground truth: before a new gate blocks anything, retro-run it against the most recent merged, human-reviewed changes under a pre-declared decision rule — at least one author-confirmed, code-change-requiring finding earns the blocking posture; zero means advisory-only with a scheduled re-evaluation — converting "seems useful" into evidence, doubling as the gate's acceptance test, and settling its authority before it acquires power.
- Review machinery manufactures work for itself: multi-lens audits structurally output "keep + improve" (zero cuts plus N new tickets is a red flag about the audit, not the product), so charge one opposed-charter role with summing the maintenance tax and rewarding deletions, require the audit synthesis template's cuts-and-freezes count, summed cost-of-ownership line, and cut-critic sign-off, and record verdict reversals with the losing arguments preserved.
- The bottleneck is a queue of human rulings: once agents accelerate implementation, throughput is often governed by sign-off latency on zero-engineering decisions, and because decisions are not "work items" no engineering board shows them on the critical path — so audit for the queue deliberately, give it an owner and deadlines, and pre-build a decision card per ruling (the single question, options with evidence, a recommendation, the timeout default, who decides) — extending the missing-inputs rule from tools to rulings.
- A fleet with a hard single-model dependency fails as a fleet: quota exhaustion mid-fan-out zeroes a batch rather than degrading it, so every routed lane pre-declares a designated alternate in a checked-in routing table asserted at dispatch preflight, every fired fallback is recorded in the handoff so quality drift stays operator-visible, a review lane's fallback must never resolve to the author's model family (defer the gate visibly instead), and the task-nature assignments themselves — reasoning to the deepest reasoner, execution to the workhorse — stay dated project policy, revisited as models change.
- **Autonomy is delegated up a ladder — verification first, the prompt last:** the four loop rungs (interactive, goal-driven, scheduled, event-driven) hand over verification, then stop condition, then trigger, then prompt — and a rung is climbed only on demonstrated verification, never granted upfront. Land it: the brief's Stop Conditions section gains three lintable lines (deterministic stop criterion, attempt/budget cap, event-or-justified-interval trigger), and the dispatch preflight fails any loop brief that leaves them empty.
- **A top-tier model is a consultant or a planner before it is the whole task — and tier access is a lease:** solo composition now carries the burden of proof, and a tier's calendar expiry is declared before anything depends on it (principle 26 at the model boundary; quota stays principle 35's). Land it: declare each lane's `composition:` in the routing table and give every model a three-field `lease:` block — `expires` (`none` is legal), `renewal_owner`, `on_calendar_expiry`.
- **The evaluator lives outside the loop it judges:** a self-improving loop fits whatever signal it can observe, so the rubric stays un-editable (principle 31) and un-fittable, and a mechanism change is accepted only on held-in plus held-out evidence. Land it: route evaluator changes through the highest gate, require both evidence fields on harness-change PRs, and fail any deletion of the only regression guard before its successor exists.
- **A negative result is evidence with an expiry date:** a failed attempt recorded at mechanism depth (direct cause, causal state, abstract mechanism) and bound to model/version/date keeps the next agent from re-running it blind — or obeying a verdict the world has outgrown. Land it: log every abandoned attempt in the negative-evidence file and make the handoff's negative-evidence field required, `none` spelled out.
- **A test lane that can skip its subject is not evidence — external-runtime skips fail closed:** a gating lane whose fixtures skip when a database or container daemon is absent reports green by asserting nothing, so treat every skip as a hidden fallback and make the dependency hard (the CI twin of principle 20). Land it: set `REQUIRE_<DEP>=1` flags unconditionally in the gating lane's command so fixtures convert skip to hard failure, assert zero skips or a pinned collected count as the lane's last step, and prove the conversion once by mutation — an unreachable dependency must turn the lane red, not green-with-skips.

## Repository Map

- `AGENTS.md`: baseline instructions for AI coding agents working in a repository.
- `docs/`: practices and rationale.
- `templates/`: copyable project files for new repositories, including
  documentation routers, module indexes, contracts, review packets, phase
  registries, prompts, and signoff docs.
- `examples/`: concrete contract, phase, review-gate, and preflight examples.
- `scripts/check_delivery_graph.py`: standard-library validation for delivery
  dependencies, shared write hotspots, and review-to-promotion edges.
- `scripts/check_session_packet.py`: fail-closed validation for independent
  Coding Agent session packets, pinned bases, dependencies, path leases,
  validation, review, integration, and retirement policy.

## Recommended Adoption Path

1. Copy `templates/AGENTS.template.md` into the project root as `AGENTS.md`.
2. Create `docs/README.md` from `templates/DOCS_INDEX.template.md` and a module
   router from `templates/MODULE_INDEX.template.md` for each active module.
3. Add `templates/NEXT_TODO.template.md` and `templates/PROGRESS.template.md` as
   bounded root snapshots that link to module-owned detail.
4. Add `templates/PHASE_REGISTRY.template.yaml` when work will span multiple
   changes, gates, or agents.
5. For multi-agent or multi-session work, instantiate
   `templates/DELIVERY_GRAPH.template.json`, validate its ready wave, and
   bootstrap gitignored `.coord/` from the coordination templates. Issue each
   independent Coding Agent session a validated
   `templates/SESSION_TASK_PACKET.template.md`.
6. When related products will converge, keep their development isolated and
   bind exact release candidates plus versioned envelopes in
   `templates/CROSS_PROJECT_INTEGRATION_PACKET.template.md`.
7. For every shared feature, start with `templates/CONTRACT.template.md`.
8. Add `templates/REVIEW_PACKET.template.md` for any design, implementation, or adoption gate.
9. Add one fast contract preflight before adding or relying on a long nightly test.
10. Split environments into local dev, scripted/fake-provider, local live, and production.
11. Move long-running workflows toward typed events, commands, activities, and current-state projections.

See [Documentation Routing and Lifecycle](docs/18-documentation-routing-and-lifecycle.md)
for module-first placement, snapshot budgets, cleanup, and incremental migration.
See [Throughput-Oriented Delivery](docs/19-throughput-oriented-delivery.md)
for top-down dependency graphs, `.coord` execution, asynchronous review,
bulk-change partitioning, related-product convergence, and periodic distillation.
See [Multi-Session Team Execution](docs/20-multi-session-team-execution.md) for
turning delivery-graph lanes into pinned, isolated, lease-bounded task packets
that a human can dispatch across several Coding Agent sessions, and for the
merge, cherry-pick, and branch-hygiene discipline that keeps one canonical
integration line.
See [Interruption-Safe Handoff and Session Resume](docs/21-interruption-safe-handoff.md)
for keeping lanes resumable when a session dies mid-task: WIP commits, per-lane
resume cards, dead-lane recovery, and the session-archaeology runbook.

## Primary References

This playbook is informed by official documentation and primary sources, including OpenAI Codex `AGENTS.md`, Anthropic Claude Code guidance, Temporal durable execution, Microsoft CQRS/Event Sourcing architecture guidance, GitHub Actions workflow scheduling, and Testcontainers/Docker testing guidance. See `docs/references.md`.
