# AI Coding Agent Collaboration

## Context Files

Use repository-local instructions to keep agents aligned:

- `AGENTS.md`: stable rules, architecture constraints, commands, verification expectations.
- `NEXT_TODO.md`: phase plan, open items, deletion gates, known blockers.
- `PROGRESS.md`: current state, recent decisions, validation, handoff notes.
- Contract docs: source of truth for shared semantics.

Keep root instruction files concise. Put detailed domain contracts in `docs/` and link to them from `AGENTS.md`.

## Task Brief Format

Each agent task should define:

- Goal
- Non-goals
- Affected contracts
- Expected files or modules
- Validation commands
- Stop conditions
- Handoff output

See `templates/AGENT_TASK_BRIEF.template.md`.

## Multi-Agent Rules

Use parallel agents only when work is owner-bounded:

- One agent can own frontend implementation.
- One can own backend contract and API.
- One can own tests and preflight.
- One can own docs and migration notes.

Avoid multiple agents editing the same contract or schema unless one lead agent owns the merge.

## Handoff Rules

Every handoff should include:

- What changed
- What was validated
- What failed or was not run
- Files touched
- Residual risks
- Next action

The next agent should be able to resume without relying on chat history.

## Prompting Agents

Good prompts ask agents to:

- Explore before editing.
- Search all usages of changed symbols.
- State the owner/source-of-truth impact.
- Add regression tests.
- Update docs.
- Report validation honestly.

Avoid prompts that ask for broad implementation without contracts, such as "make the workflow stable" or "fix all state bugs." Convert them into bounded contract and owner tasks.

