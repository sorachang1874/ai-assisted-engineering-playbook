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
- Documentation is runtime infrastructure: `AGENTS.md`, `NEXT_TODO.md`, `PROGRESS.md`, contracts, and signoff docs should stay close to the code.
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
- Attribute a failure before you own it: re-run a post-change test failure on the pinned baseline before debugging — identical failure means pre-existing, recorded in a known-failure budget, not a regression you introduced.
- Prefer deletion to wrapping, and classify before you sweep: remove a dead dual path instead of rewriting it; for a large mechanical sweep, scout and adversarially verify each site (read vs write) before editing, preserving the surviving path's exact no-row/error sentinel.
- Minimize gate round-trips, not findings per round: a cross-model gate round is serial and high-latency, so front-load discovery with parallel self-review lenses over every surface the gate audits, fix each finding's whole class and the ripple of any canonical change in one round, and batch the long tail into a single confirming gate instead of a round-trip per cited line.
- Couple a component to its safety enforcement (fail closed when absent): a component whose safety depends on a separate enforcement (firewall/allowlist, network policy, sidecar) must hard-depend on it and refuse to start/serve unless the enforcement is provably in effect — assert the specific rule/chain exists, not just that the enforcement service started — so a missing enforcement fails closed (component down), not open (component running unprotected).
- Validated is not delivered — verify at the surface the consumer reads: when one source fans out into several generated artifacts, prove a file is the source (regenerate-and-diff) before editing it, verify a change in the artifact the consumer *actually* loads (not the intermediate the test/checker reads), and make propagation one command plus a regenerate-and-diff drift guard so no derived copy silently rots.
- Live coordination is ephemeral; the durable truth is git: when long-lived agents share a repo, keep the live channel (task claims, heartbeats, questions) local and gitignored, but promote every normative decision (frozen contract, ratified principle, ownership change) into git — a decision left only in the live channel is invisible to the next agent, instance, and session.
- Merged is not landed — verify integration by content: a PR shown as "merged" can leave later or stacked commits stranded in no open PR and not in `main` (squash collapses to the base at merge time, and `git --merged` ancestry misleads across squashes); confirm the cutoff by grepping `origin/main` for known content markers, stop pushing to a merged branch, and rebase on main after any peer merges.
- Separate diff hygiene from refactor appetite: diff hygiene is universal (match the file's style, never reformat untouched code, no opportunistic orthogonal edits — every changed line traces to the task or a named refactor); refactor appetite scales with codebase maturity (a stable codebase favors minimal-diff conservatism, an early-stage one welcomes bold redesign and early abstraction toward an articulated reuse), and what makes aggressive refactoring safe is bounding it — named, scoped, own-PR, contract-first — not avoiding it.

## Repository Map

- `AGENTS.md`: baseline instructions for AI coding agents working in a repository.
- `docs/`: practices and rationale.
- `templates/`: copyable project files for new repositories, including
  contracts, review packets, phase registries, prompts, and signoff docs.
- `examples/`: concrete contract, phase, review-gate, and preflight examples.

## Recommended Adoption Path

1. Copy `templates/AGENTS.template.md` into the project root as `AGENTS.md`.
2. Add `templates/NEXT_TODO.template.md` and `templates/PROGRESS.template.md`.
3. Add `templates/PHASE_REGISTRY.template.yaml` when work will span multiple
   changes, gates, or agents.
4. For every shared feature, start with `templates/CONTRACT.template.md`.
5. Add `templates/REVIEW_PACKET.template.md` for any design, implementation, or adoption gate.
6. Add one fast contract preflight before adding or relying on a long nightly test.
7. Split environments into local dev, scripted/fake-provider, local live, and production.
8. Move long-running workflows toward typed events, commands, activities, and current-state projections.

## Primary References

This playbook is informed by official documentation and primary sources, including OpenAI Codex `AGENTS.md`, Anthropic Claude Code guidance, Temporal durable execution, Microsoft CQRS/Event Sourcing architecture guidance, GitHub Actions workflow scheduling, and Testcontainers/Docker testing guidance. See `docs/references.md`.
