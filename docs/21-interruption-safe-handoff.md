# Interruption-Safe Handoff and Session Resume

Sessions die mid-task: quota walls, crashes, expired model leases, closed
laptops. The cost is not paid by the dying session — it is paid by whoever
resumes the lane, often a different tool or model family with zero shared
context. When the lane's plan, partial edits, and current state exist only in
the dying session's context, the resumer pays **session archaeology**: hours
of forensic reconstruction before the first useful edit.

The playbook already asks the question — Blindspots prompt 3
(`16-loops-and-model-composition.md`): "If this session dies mid-task, where
do its notes, decisions, and partial results already live on disk?" — and
states the principle (`01-agent-collaboration.md`: the next agent resumes
without chat history; run-id checkpoint-resume for fan-outs in
`16-loops-and-model-composition.md` § Loop Hygiene). This doc is the
operational answer for a single lane: four recording habits that make
interruption cheap, plus the archaeology runbook for when they were skipped.

Observed shape: a forked remediation session died at an account quota wall
four minutes after fork, leaving an uncommitted source edit, a stale digest
pin that broke validation, and no regression tests. The plan that created it —
a two-surface remediation split across two sibling projects — existed only as
one message in a 174 MB orchestrator session log. The resuming agent, a
different tool entirely, spent its first stretch reconstructing instead of
editing. Each habit below is the cheap version of something the archaeology
had to do the expensive way.

## Record the Plan When It Is Decided, Not When It Completes

The durable-truth rule (`14-async-multi-agent-collaboration.md`: promote
normative decisions to git) has an in-flight twin: **a dispatch decision is
durable only when it exists outside the dispatcher's context.** The moment the
lead decides a surface split, wave plan, or fork charter, write it where the
lanes live:

- the checked-in delivery graph, when the split changes dependencies, write
  sets, or hotspots; or
- `.coord/` — a log entry, board row, or per-lane handoff stub — when it is
  execution state for the current run.

Write it **before** forking the sessions that execute it, not inside the same
message that forks them: a fork's charter stored in the parent's context does
not survive the parent. The test is one sentence: if every session involved
died right now, could a stranger redraw the split from disk alone?

## Land Work as Commits, Not Dirty Bytes

Uncommitted work is invisible to everything that coordinates the lane: the
path lease, the board, the lead's sweep, and the resumer. It is attributable
only by mtime forensics and recoverable only by someone with access to that
exact filesystem.

- Commit to the lane branch at every natural boundary: after each validated
  step, before any pause, before any context-heavy detour. `wip:` commits are
  legal on lane branches — integration consumes a commit or an immutable
  handoff (`20-multi-session-team-execution.md`), never copied dirty files, so
  a messy lane-branch history costs nothing and a clean one buys nothing.
- A WIP commit that fails validation still beats dirty bytes: it is diffable,
  attributable, and resumable. Record what is broken in the resume card
  (below), not only in the final message the session may never get to send.
- **Fork-time rule:** when a parent forks a sub-session, the fork's first
  durable act — before its first edit — is writing its charter and inherited
  state to its handoff path or status file.

## Keep a Resume Card per Active Lane

The per-agent status file (`14-async-multi-agent-collaboration.md`) is written
for the lead's sweep; it must also serve a **cold resumer on a different
tool**. Update it at every commit boundary. Fields:

```text
lane / packet id+version:
goal (one sentence) and deliverable:
base commit / branch / worktree:
touched paths so far:
last validation: <exact command> -> <actual result>
state: what works; what is broken or half-applied
next step: the single next action
```

Rules: no references to conversation ("as decided above" names nothing on
disk); exact commands, not descriptions of commands; an unknown field is
written as `unknown`, never omitted. A card that needs the dying session's
context to interpret has already failed its purpose.

## Recovering a Dead Session's Lane

When a lane goes silent past its `expected-done`, the integration lead
recovers before redispatching:

1. Read the resume card and handoff path. If they answer goal, state, and next
   step, resume is cheap — hand them to the successor session.
2. Inspect the lane branch: its WIP commits are the ground truth of how far
   the session got; `git status` in its worktree shows what never landed.
3. Rerun the card's last validation command. Its result — not the dying
   session's claim — is the lane's state.
4. Decide: resume (issue a new packet version pinned to the WIP head, carrying
   the card forward) or retire per the stale-packet rules
   (`20-multi-session-team-execution.md`). A dead session is not automatically
   a stale packet; time expiry alone does not authorize takeover.

## Session Archaeology Runbook (When Records Are Missing)

When the card, the commits, and the plan artifacts are all absent,
reconstruct from session logs instead of guessing. For Codex CLI rollouts
(`~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`, one JSON payload per line):

1. **Find candidate sessions by keyword.** `grep -l "<distinctive term>"` over
   the session directory, then sort by modification time. Multi-hundred-MB
   rollouts grep fine; do not open them in an editor.
2. **Identify forks.** Each file's `session_meta` payload carries
   `forked_from_id` / `agent_path`; children of a known parent id are the
   dispatched lanes. A fork whose file stops minutes after its start, with no
   closing summary, is the interrupted one.
3. **Reconstruct plans and verdicts from `agent_message` payloads** — final
   answers and commentary — not from reasoning traces: the surface split and
   the review verdicts live in the parent's last few agent messages.
4. **Attribute uncommitted edits by timestamp correlation:** an edit whose
   mtime falls inside exactly one session's active window (its rollout file's
   first-to-last timestamp) belongs to that lane.
5. **Backfill, then fix the habit.** Write the reconstructed state into the
   lane's resume card and handoff path *before* editing code, and record any
   archaeology run over ~30 minutes as a distill candidate
   (`19-throughput-oriented-delivery.md` § Continuous Distillation): the
   missing record is the defect; the reconstruction is its cost.

Other harnesses keep analogous records (transcript JSONLs, headless session
logs); the technique transfers: metadata first for topology, final-answer
messages for intent, mtimes for attribution.

## Checklist

- [ ] Every dispatch decision (surface split, wave plan, fork charter) exists
      in the delivery graph or `.coord` before the sessions executing it start.
- [ ] Lane branches carry WIP commits at every boundary; no lane's only copy
      of progress is a dirty worktree.
- [ ] Each active lane's status file holds a current resume card that a cold,
      different-tool resumer can execute from.
- [ ] A forked session writes its charter to disk before its first edit.
- [ ] Dead-lane recovery reads card → branch → validation before deciding
      resume versus retire; death alone does not retire a packet.
- [ ] Any archaeology run backfills the missing records first and lands a
      distill candidate for the recording gap.
