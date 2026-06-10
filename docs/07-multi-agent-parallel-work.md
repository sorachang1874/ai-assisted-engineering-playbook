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

### Cross-Model Review Runbook (Codex)

Reviewer independence is strongest when the reviewer is a **different model
family** than the author (e.g. Codex/GPT reviewing Claude's output, or vice
versa). Different models have different blind spots; in practice cross-model
review has caught blockers the author's own model family repeatedly missed.

Proven configuration (validated 2026-06; revisit when models change):

- **Model `gpt-5.5`, reasoning effort `xhigh`, service tier `fast`.** Review
  DEPTH is governed by the reasoning effort; the service tier only changes
  serving latency — so fast mode keeps review quality while cutting wall-clock.
  Quota note: when another agent (e.g. Claude Code) is the primary dev driver,
  Codex spend is nearly all reviews, which makes the fast tier affordable.
- Gotcha: on ChatGPT-account Codex, `-m gpt-5.5-fast` is **not a valid model**
  (400). The correct knob is the `service_tier` config key. Validate config
  keys cheaply with `--strict-config` before relying on them.

Canonical one-shot invocation:

```bash
codex exec --sandbox read-only \
  -c model_reasoning_effort="xhigh" -c service_tier="fast" \
  "<standing REVIEW_BRIEF + changed files + change-specific questions>" \
  < /dev/null > review.out 2>&1
```

Operational rules (each root-caused the hard way):

- **Always redirect stdin (`< /dev/null`).** A "hung" `codex exec` that sits
  for 20+ minutes at 0% CPU is usually blocked reading stdin, not slow
  reasoning. With stdin closed, xhigh completes multi-file reviews in minutes.
- **Never pipe codex through `tail`/`head`** — they buffer until EOF and hide
  all progress. Redirect to a file and read the file.
- Wrap in a hard `timeout` as a backstop; always `--sandbox read-only` so the
  reviewer can never edit (reviewer-independence rule above, enforced).
- Start every prompt with a **standing review brief** (principles, goals,
  constraints, output format) so single-shot reviews need no chat history,
  then append the packet per the Required Review Packet checklist.
- Reserve the interactive Codex CLI for the rare review too large or too
  iterative for one shot.
- Set the same defaults machine-side (`~/.codex/config.toml`: `model`,
  `model_reasoning_effort`, `service_tier`) so ad-hoc invocations match the
  documented gate configuration; per-invocation `-c` still overrides.

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
