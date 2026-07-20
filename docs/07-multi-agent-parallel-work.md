# Multi-Agent Parallel Work

This doc covers the **fan-out** topology: a lead splits bounded tasks to workers (or sub-agents) and
reads results back. For the different case of **several long-lived agents — separate interactive CLI
processes, no shared event loop — working one repo concurrently with a human as the only merge gate**,
see `14-async-multi-agent-collaboration.md` (live-channel-vs-git memory, lead-pulls coordination,
verify-merged-by-content).

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

### Dispatch Preflight (before fan-out)

A fleet with a hard single-model dependency fails *as a fleet* — quota exhaustion mid-fan-out
zeroes the batch instead of degrading it (principle 35). So before fanning tasks out, the lead
asserts the model routing is declared in the checked-in routing table
(`templates/MODEL_ROUTING.template.yaml`):

- A checked-in delivery graph exists for work spanning more than one lane, and
  `python scripts/check_delivery_graph.py <graph> --ready` passes. Dispatch only
  the printed ready wave. The graph, not agent availability, decides width.
- Every lane declares exact writes, validation, a stop condition, and a handoff;
  shared write paths have one registered hotspot, integration owner, and
  dependency-ordered writer list. An unregistered overlap fails dispatch.
- The routing table exists.
- Every lane names a fallback.
- No review lane's fallback resolves to the author's model family — the independence lane of
  principle 14 is a constraint, not a preference: defer the gate visibly rather than substitute
  the author's family and call the result independent review.
- Every model in the table carries a lease block and no lane's primary is past its declared
  `expires` (principle 37; `16-loops-and-model-composition.md`) — a missing lease block or an
  expired primary fails; `expires: none` (owned/self-hosted tiers) is legal and passes.
- A brief that launches a loop — goal-driven, scheduled, or event-driven (principle 36;
  `16-loops-and-model-composition.md`) — has all three `## Stop Conditions` lines filled: the stop
  criterion, the attempt/budget cap, and the trigger. A loop brief that leaves any of the three
  empty fails.
- A fan-out above the threshold — more than 5 agents, or a projected spend above $50 (both
  thresholds repo-configurable) — ran a pilot slice before the full-width launch
  (`16-loops-and-model-composition.md` § Loop Hygiene; principle 32's retro-validation applied to
  fan-outs). A full-width launch that skipped the pilot fails; the handoff's pilot-findings field
  records what the pilot changed in the full run's configuration.
- A relaunch after an interrupted fan-out names the run id it resumes from and re-dispatches only
  lanes with no completed checkpoint (`16-loops-and-model-composition.md` § Loop Hygiene) — a
  relaunch that would re-run a completed lane fails, and the handoff's resumed-from field records
  the lanes re-dispatched.

The complete planning and scheduling protocol is in
`19-throughput-oriented-delivery.md`. Use
`templates/DELIVERY_GRAPH.template.json`; do not reconstruct dependencies or
partition maps separately in worker prompts.

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

Standing model policy (2026-07-10, supersedes the 2026-06 pinned combo):

- **The review gate always runs the NEWEST available model at the HIGHEST
  reasoning effort — never pin a model/effort/tier inside gate scripts or
  docs.** The single place that tracks "latest + max" is the operator-maintained
  codex global config (`~/.codex/config.toml`); gate scripts inherit it and
  RECORD the effective model/effort into each review report (auditability:
  every verdict is attributable to a model+effort). Pinning inside scripts is
  how a gate silently decays — we caught a gate running a new model at a stale
  pinned effort, i.e. paying for less review depth than the operator intended.
  (Reference point when this policy was written: `gpt-5.6-sol` + effort
  `ultra` + tier `fast`. The 2026-06 validated combo `gpt-5.5`+`xhigh`+`fast`
  is history — do not copy pins forward.)
- Review DEPTH is governed by the reasoning effort; the service tier only
  changes serving latency — fast tier keeps review quality while cutting
  wall-clock. Quota note: when another agent (e.g. Claude Code) is the primary
  dev driver, Codex spend is nearly all reviews, which makes fast affordable.
- Gotcha: on ChatGPT-account Codex, a model-name suffix like `-fast` is **not
  a valid model** (400). The correct knob is the `service_tier` config key.
  Validate config keys cheaply with `--strict-config` before relying on them.

Canonical one-shot invocation (NO pinned `-c` model/effort flags — inherits
the global config; explicit env-var overrides are for A/B experiments only):

```bash
codex exec --sandbox read-only \
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
- Deviations (Assumptions' in-flight twin — empty ⇒ write `none`; each carries a regression
  test pinning the chosen behavior, and a deviation that changes contract direction is a stop
  condition, not a deviation; see `15-finding-your-unknowns.md`)
- Contract changes
- Follow-up needed
- Model used / fallback fired? (a silent model downgrade is a hidden fallback — principle 2 —
  so a fired fallback stays operator-visible here; principle 35)
- Consults (one line per advisor consult — juncture · question · ruling · cost; zero consults on a
  brief that declared junctures is a Deviations check, and zero on a fork-free task is the advisor
  economics working; principle 37, `16-loops-and-model-composition.md`)
- Negative evidence (required — attempts abandoned during this dispatch land as rows in
  `templates/NEGATIVE_EVIDENCE.template.md`; write the literal word `none` when there were none, a
  blank fails the dispatch preflight; principle 39)
- Pilot findings (required for an above-threshold fan-out — what the pilot slice changed in the
  full run's configuration: per-agent budgets, fallback rules, stall points;
  `16-loops-and-model-composition.md` § Loop Hygiene)
- Resumed from run id / lanes re-dispatched (only on a relaunch after an interrupted fan-out —
  name the run id the relaunch resumed from and the lanes it re-dispatched, so a rerun of an
  already-completed lane is visible at review; `16-loops-and-model-composition.md` § Loop Hygiene)

The lead agent should not rely on chat memory. It should be able to verify from files and commands.

This artifact closes *completed* work. A session interrupted mid-task cannot produce it, so the
in-flight unit of handoff is smaller and earlier: WIP commits on the lane branch plus a current
resume card in the status file — see `21-interruption-safe-handoff.md`.

## Conflict Prevention

Before parallel work:

- Lock contract docs.
- Assign file ownership.
- Define validation commands.
- Define no-touch areas.
- Define merge order — and the mechanism per boundary: cherry-pick lane commits by default,
  rebase only on a lane's own branch, never rewrite the integration branch
  (`20-multi-session-team-execution.md` § Merging and Version Control for Lane Work).
- Register every shared write hotspot in the delivery graph; "coordinate while
  both edit it" is an unmodelled serialization edge, not a parallel plan.

## Agent Failure Modes To Plan For

- Sessions die mid-task with their state in their own context: a quota wall,
  crash, or expired model lease kills the session and everything it never
  wrote down. One forked remediation session died at a quota wall four minutes
  after fork, leaving an uncommitted source edit, a stale digest pin that
  broke validation, and a split plan that existed only in its parent's session
  log; the resumer — a different tool entirely — paid session archaeology
  before its first edit. The defense is recording, not redundancy: commit WIP
  to the lane branch at every boundary, keep the resume card current, and
  record the dispatch plan before forking
  (`21-interruption-safe-handoff.md`).

- Output-size limits kill whole-file emitters: an agent asked to produce a
  large precision file (hundreds of lines of fail-closed logic) can
  repeatedly hit its per-response output cap trying to write it in one shot
  and die without producing anything. Either instruct chunked writes
  explicitly, scope the task smaller, or be ready for the lead to take the
  task over directly — and check intermediate filesystem state when an
  agent goes quiet, rather than waiting on its final message.
- Parallel producer/consumer agents drift at the seam: when one agent
  builds the artifact producer and another builds its consumer, pin the
  exact shared field names in BOTH prompts, review the seam yourself at
  merge, and add one cross-module test that feeds real producer output into
  the real consumer (twin hand-rolled fixtures keep both suites green while
  the interface breaks).
- The lead's merge review is part of the work, not overhead: agents
  faithfully implement what the spec says, including its gaps; the
  highest-value findings after a parallel round usually sit in the
  specified-but-unstated corners (unreachable statuses, missing
  cross-checks), which is what the post-merge adversarial critique pass is
  for.
- A parallel understand-map is necessary but not sufficient: a fan-out of
  reader agents that maps the machinery, boundaries, and existing tests will
  still miss consumers — direct-call contract tests, a second suite
  exercising the same surface — because each reader only sees its slice.
  Treat the map as a starting set, then run the full affected test suite to
  surface the consumers no reader named, and fold the missed ones in before
  claiming the change is covered.
- A classify-then-edit sweep needs the classification verified, not just
  produced: when one agent scouts hundreds of edit sites and labels each
  (safe to change vs defer), have an independent pass try to *refute* each
  "safe" label before the lead edits. A scout map that is merely "probably
  right" mis-edits the one site that looked safe but was not (principle 17).
  The dispatch table the workers edit from must then be *generated* by
  script from the verified recon artifacts, never re-typed: on one
  domain-retirement batch a hand-typed rename map dropped one method from
  the verified listing, re-introducing an error after the adversarial
  pass — workers read the table, not the recon, so verify at the surface
  the consumer reads (principle 21). Every worker brief carries the
  closed-world clause — a site not in the table is reported as ambiguous
  in the handoff, never guessed — which is what caught that orphan: one
  worker reported the unlisted site instead of improvising on it (the
  pasteable line lives in `templates/AGENT_TASK_BRIEF.template.md`
  § Constraints). Closeout then reconciles every reported-ambiguous site
  against the recon.
