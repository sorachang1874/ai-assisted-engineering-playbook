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

## Independent Review Gate

Use a separate reviewer for gates that change contracts, evidence semantics,
generated output chains, risky execution, secrets, publication, defaults, or
production claims.

The reviewer should receive a review packet, not a vague instruction to "look
over the code." The packet should include:

- gate type: Design, Implementation, or Adoption;
- objective and non-goals;
- contracts and schema changes;
- artifact chain from raw input to downstream status or publication;
- evidence classes;
- boundary flags;
- validation commands and exact results;
- claims to verify or reject.

See `templates/REVIEW_PACKET.template.md` and
`examples/review-gate-packet.md`.

Do not ask for a narrow script review when the real risk is in downstream
queues, handoffs, reports, manifests, or default configuration. Conversely, do
not treat a design review as implementation or adoption approval.

### Reviewer Independence Rules

The reviewer should be operationally independent from the implementer:

- Give the reviewer a bounded packet, file list, artifacts, tests, and claims
  to verify.
- Ask for `NO-GO`, `GO WITH FIXES`, or `GO`.
- Instruct the reviewer not to edit files unless the task is explicitly a
  delegated implementation task.
- Prefer read-only validation commands and artifact inspection for gate review.
- Record the final verdict and scope in a durable review index or progress log.
- Treat `GO WITH FIXES` as a blocked gate until the fixes are implemented and
  re-reviewed.
- Treat each `GO` as scoped only to the named gate.

Independent review is most valuable before a milestone is adopted, not only
after a small script is written. Trigger it for:

- contract or schema changes;
- milestone implementation or completion;
- evidence semantics changes;
- output-chain, cache, report, queue, or manifest changes;
- external calls, remote execution, scheduling, publication, or default changes;
- secret or private-resource handling;
- effectiveness, production-readiness, or user-facing claims;
- dependency/toolchain changes that affect execution or evidence collection.

If a user corrects the design boundary after implementation has begun, add that
boundary as a future review-gate trigger instead of relying on manual memory.

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
