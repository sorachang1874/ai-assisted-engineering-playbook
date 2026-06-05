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
- Model output is a contract: version prompts, validate output against a schema at the boundary, and keep records for review and rollback.
- User-invisible fallback stays operator-visible: a graceful fallback for the user must still be logged, counted, and surfaced so it never becomes a silent normal path.
- Secrets stay server-side and out of commits and logs; runtime mode comes from one central config, not scattered env vars.

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
