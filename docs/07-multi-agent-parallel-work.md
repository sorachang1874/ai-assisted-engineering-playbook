# Multi-Agent Parallel Work

## When Parallel Agents Help

Parallel agents help when tasks are independent and contracts are stable:

- Frontend and backend implementation after API contract is fixed.
- Test harness and product UI polish.
- Documentation and code migration.
- Static review and implementation.

## When Parallel Agents Hurt

Avoid parallel edits when:

- The contract is still unresolved.
- Multiple agents need the same schema or shared type.
- Ownership of source of truth is unclear.
- Migration bridge behavior is still being decided.
- Validation requires one coherent runtime state.

## Lead Agent Pattern

Use one lead agent to own:

- Contract decision
- Task splitting
- Merge order
- Final validation
- Progress summary

Worker agents own bounded outputs and hand off changes.

## Handoff Artifact

Each worker handoff should include:

- Task goal
- Files changed
- Tests run
- Failures
- Assumptions
- Contract changes
- Follow-up needed

The lead agent should not rely on chat memory. It should be able to verify from files and commands.

## Conflict Prevention

Before parallel work:

- Lock contract docs.
- Assign file ownership.
- Define validation commands.
- Define no-touch areas.
- Define merge order.

