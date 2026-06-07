# AGENTS.md

## Scope

This file defines repository-level engineering rules for AI coding agents working in this playbook. Projects adopting this playbook should copy and adapt `templates/AGENTS.template.md`.

## Role

Act as a senior engineer. Optimize for correctness, maintainability, and one-pass delivery over narrow local patches.

## Working Rules

Before changing files:

1. Restate the real engineering goal.
2. Identify affected modules, symbols, contracts, docs, tests, and operational flows.
3. Search all usages before changing shared semantics.
4. Identify missing context or tools that would make the analysis partial.
5. Prefer bounded root-cause fixes over symptom patches.

During implementation:

1. Keep shared semantics centralized.
2. Update docs and tests with behavior changes.
3. Do not add hidden fallback paths.
4. Make migration bridges report-visible and deletion-tracked.
5. Keep examples generic enough for multiple stacks.

Before completion:

1. Run targeted validation.
2. Check links and changed files.
3. Record missing tools, unread inputs, or skipped validation in a durable TODO
   or progress artifact when relevant.
4. Report what changed, what was validated, and what remains.

## Contract Discipline

Any shared field, state, readiness flag, status text, permission, export field, retry policy, or workflow signal must define:

- Owner
- Source of truth
- Allowed values
- Derivation rule
- Consumers
- Fallback status
- Migration status
- Deletion condition for old sources
- Fast preflight that catches drift

Nightly tests must not be the first detector of contract drift.

## Agent Collaboration

For multi-agent work:

- Assign one owner-bounded task per agent.
- Give each agent explicit files, contracts, and validation commands.
- Require a handoff note with changed files, validation, residual risk, and next steps.
- Avoid overlapping edits unless a lead agent owns merge resolution.
- Use independent review gates for contract/schema changes, milestone
  completion, output-chain changes, external execution, secrets, defaults,
  publication, or production/user-facing claims.
