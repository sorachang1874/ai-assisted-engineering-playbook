# Asynchronous Multi-Agent Collaboration (Separate Long-Lived Agents)

Docs `01` and `07` cover the **fan-out** topology: one orchestrating context spawns sub-agents
(or a lead splits bounded tasks to short-lived workers) and reads their results back. This doc
covers a different, harder topology that recurs in practice:

> **Several long-lived agents — separate interactive CLI processes, each its own context window,
> no shared memory and no shared event loop — working the same repo concurrently, with one human as
> the only merge gate.**

This is the shape you get when a non-engineer founder runs two or three Claude Code (or Codex)
instances in separate terminals over days. It looks like the fan-out model but breaks three of its
hidden assumptions, and the corrections below are what keep it from drifting. Everything here was
validated on a real multi-week project (one founder + a lead instance + module-builder instances).

## The assumption that breaks: there is no shared runtime

In the fan-out model the orchestrator *can* message its sub-agents — they share a process and an
event loop. Separate CLI instances do **not**. There is no daemon reading one agent's heartbeat file
and waking another. So:

- **"Heartbeat automation" does not exist in this topology.** A status/heartbeat file is a *passive
  shared file*; it transmits information only when some agent is independently triggered and happens
  to read it. Designing around an imagined push channel ("the lead will be notified when CC2 pushes")
  is the first mistake — that notification never fires on its own.
- **The human is the bus.** The only thing that reliably triggers an idle CLI instance is the human
  typing into it. Treat the founder's attention as the scarce, real coordination primitive and design
  to *minimize* it, not to assume an automated substitute.

The naive fix — "have the founder copy each agent's PR body and logs into the lead" — turns the human
into a manual message bus, which does not scale past a couple of exchanges. The correct fix inverts it:

> **Lead pulls; the human only pings.** The lead instance has shell + `gh` + filesystem access, so a
> one-word ping ("CC2 pushed") is enough — the lead then runs its own sweep: `gh pr list`, read the
> shared coordination dir, diff its own owned paths. The human never copies a PR or log body; the lead
> reads them itself. A scheduled self-sweep (a recurring prompt every N minutes) keeps the lead current
> even between pings, so "what's the state of the project?" is always answerable without the human
> assembling it.

## Two layers: live channel vs durable memory (and the promotion discipline)

The single most important structural rule for this topology:

| Layer | Where | Holds | Survives a fresh clone / new session / new instance? |
| --- | --- | --- | --- |
| **Live coordination** | a small **gitignored, local** dir (`.coord/`) — a board, per-agent status files, an append-only log | task claims, heartbeats, questions, decisions-in-flight, "I merged X" | **No** — ephemeral, this-machine-only |
| **Durable truth** | **git** — contract files, `AGENTS.md`, the project-status snapshot, `docs/` | contracts, principles, ownership, milestone state | **Yes** |

Why a local dir for the live channel instead of using git as the transport: for agents co-located on
one machine it removes every git race (no push-reject loops, no commit-from-a-feature-branch
gymnastics, no stale `origin/main` reads). Both instances read and write the same absolute path; the
human opens it in any editor.

The trap this creates, and its discipline:

> **A decision that lives only in the live channel is invisible to every agent that wasn't watching at
> that moment** — and to every future instance. So when a `.coord/` decision becomes normative (a frozen
> contract, a ratified principle, an ownership change), the author must **promote the normative form to
> git** — the contract file, a `docs/` doc, `AGENTS.md` — and only *announce* it in the live log. The
> live channel is the bus; **git is the memory.** When the two disagree, an agent trusts git.

A practical SSOT that makes this work: one Lead-maintained **project-status snapshot in git** — the
"where is the whole project" doc every agent reads at the start of every work chunk. Enforce the
"read it first" habit in `AGENTS.md` itself, so a fresh instance self-orients without the human
re-explaining. (Don't rely on per-prompt reminders; encode the habit in the standing rules.)

The same rule covers in-flight execution plans: a surface split, wave plan, or fork charter that
exists only in the orchestrator's session context is invisible even to its own dispatched lanes —
record it in the graph or `.coord/` when it is decided, before the sessions executing it start
(`21-interruption-safe-handoff.md`).

## The live channel, concretely

A minimal file-based channel needs no broker, daemon, MCP, or A2A layer — deliberately. Two or three
agents plus a human do not need lease machinery; they need clear ownership and an append-only log.

```
.coord/                 # gitignored, local, both instances read/write the same path
  README.md             # the rules in brief (read first)
  BOARD.md              # lead-owned live projection of the checked-in delivery graph
  status-<agent>.md     # one per agent; an agent writes ONLY its own (heartbeats never collide)
  handoffs/<lane-id>.md # immutable handoff per completed attempt
  distill/<stamp>-<agent>.md # append-only failure/inefficiency candidates
  log/
    NNN-<author>-<kind>.md   # append-only ledger; never edit a published entry
```

Conventions that prevent the races:

- **The checked-in delivery graph owns scheduling; the board only projects it.**
  Dependency edges, write paths, hotspots, gate policy, and promotion edges are
  normative and lead-owned in Git. The board may say who is active, but cannot
  make an incomplete lane ready. Validate and dispatch only the graph's ready
  wave (`19-throughput-oriented-delivery.md`).

- **Per-agent status files, never a shared status block.** Each agent edits only its own file, so two
  agents never contend on the same line. Last-writer-wins is fine for the board because the
  one-owner-per-row map means the two agents edit *different* rows.
- **The status file doubles as the lane's resume card.** It has two readers: the lead's sweep, and a
  cold resumer — possibly a different tool or model family — picking the lane up after its owner dies
  mid-task. It must carry goal, base commit, touched paths, last validation, state, and next step,
  with no references to conversation; the card format and the dead-lane recovery protocol are in
  `21-interruption-safe-handoff.md`.
- **Append-only log with author-embedded filenames.** `NNN-<author>-<kind>.md` means two agents writing
  at the same instant produce *distinct* files — no lost update, no locks. To revise a published entry,
  append a `correction` referencing the old number; never edit it in place.
- **Monotonic, global log numbering.** Numbering per-author causes collisions (a `056-cc2` and a
  `056-lead` both appear). The next number is `max(existing) + 1`, period.
- **Per-task `verify:` on the board.** Every task row carries the objective command/criteria that
  closes it, so an agent can self-terminate and the human can audit "done" without reading the diff.
  (This is the per-task instance of the global definition-of-done evidence gate.)
- **Per-task `expected-done:` on the board.** Every row carries a predicted completion time; the
  sweep checks a running loop against it, so a stalled or drifting loop is sweep-visible rather than
  quietly dead (principle 36; `16-loops-and-model-composition.md`). A row past its `expected-done`
  with no closing `verify:` is the sweep's cue to inspect, not to wait.
- **A request template so a cross-agent ask is actionable in one read.** A cross-boundary request
  carries: *what is needed · why · the exact file/contract · a suggested change · the single decision
  the lead must make*. A vague "can you look at this?" costs a round-trip; a precise patch-shaped ask
  closes in one.
- **Hygiene as a standing chore.** Archive the log once it passes ~20 entries; keep the board to *active*
  tasks only (done milestones sink into the project-status snapshot). A live channel that accretes
  forever stops being read.
- **Distill without interrupting delivery.** Any agent may append a candidate
  for a repeated failure or avoidable-work mechanism. A separate lead-scheduled
  lane synthesizes candidates at milestone/weekly triggers; raw observations do
  not mutate the active plan or become principles by themselves.

## Why one lead, not N equals

Parallelize only the genuinely **independent** module tracks. Anything inherently **sequential** —
contract design, planning, cross-cutting integration — is owned and serialized by a single lead. The
contract-freeze-before-fan-out rule (doc `02`, doc `07`) is what makes the parallel tracks safe:

1. The lead authors and **freezes** the shared contract in git, and merges it *before* any builder
   writes code against it.
2. Builders import contracts **read-only**; a builder **never edits a contract in its own branch**.
3. A mid-flight contract change goes through the lead only: the lead merges it, announces it in the
   live log, and builders **rebase before continuing**. This is the explicit counter to the dominant
   failure mode — peers making conflicting implicit assumptions, so each branch "looks done" but does
   not integrate.
4. A builder that needs a field the lead owns files a `question`; it does **not** reach across the
   ownership boundary.

For a vocabulary/shape refactor that must keep a legacy artifact byte-identical while new work moves to
the new model, freeze the contract **slice by slice** rather than in one big bang: per slice, the lead
freezes the contract, the owner implements, and a **double-run equivalence test** proves the legacy path
is unchanged while the new path produces the intended result (determinism checklist:
`03-testing-strategy.md` § Determinism Checklist for Double-Run Equivalence). Mark the compatibility
layer *transitional* with an explicit deletion gate (e.g. "remove the legacy union once the last
lesson using it retires") — not a permanent fixture (principle 17).

## Integration discipline (separate-process specifics)

The fan-out integration rules (worktree + branch + PR per task, own port + test DB, small PRs, never
break main, never auto-merge, human merges after reading the diff) all carry over. Two additions matter
specifically when long-lived agents push to the same remote:

- **After any peer's PR merges, the other agent rebases its feature branch on main before continuing.**
  Stale-base divergence is the silent cost of long-lived parallel branches.
- **Merged is not landed — verify a squash captured what you think, by content** (principle 23). This
  bit hard: a worker PR squash-merged *early* captured only part of a long-lived branch; continued
  pushes then sat in no open PR and not in main — silently stranded, and masked because the demo still
  ran from the branch. The true cutoff was found only by grepping `origin/main` for content markers, not
  by trusting the squash message or "where I thought it was." Rule: stop pushing to a merged branch; open
  a fresh PR for continued work; and confirm what a squash captured by grepping the merged content.

## What to deliberately *not* build

For two or three co-located agents plus a human, resist the urge to add infrastructure:

- No coordination daemon/broker (extra process, auth dependency, localhost-only).
- No MCP advisory-lease machinery (built for many agents on one big refactor; the one-owner-per-path map
  is enough here).
- No A2A protocol layer (heavyweight for a handful of peers).
- No parallelizing of contracts/planning (sequential reasoning degrades sharply when split).

The whole point of this topology is that a tiny file-based channel + git-as-memory + a human merge gate
is *sufficient*, and that adding brokers trades a real, debuggable simplicity for imagined automation
that the separate-process reality does not actually deliver.

## Checklist

- [ ] One lead owns contracts, integration, and the merge recommendation; builders own bounded tracks.
- [ ] Live coordination is a gitignored local dir; durable truth is git; normative decisions are
      **promoted to git**, not left in the live channel.
- [ ] A Lead-maintained project-status snapshot lives in git; `AGENTS.md` makes "read it first" a
      standing rule.
- [ ] Lead pulls (gh + filesystem); the human only pings and merges. A scheduled self-sweep keeps the
      lead current.
- [ ] Per-agent status files; append-only log with global monotonic numbering; per-task `verify:`
      and `expected-done:`; a patch-shaped request template; periodic archival.
- [ ] A checked-in, lead-owned delivery graph validates dependencies, exact
      writes, hotspots, review/promotion edges, and the ready wave; `.coord` is
      only its live projection.
- [ ] Contracts frozen before fan-out (slice by slice for refactors, with a double-run equivalence test
      and a deletion gate for any transitional compatibility layer; determinism checklist:
      `03-testing-strategy.md`).
- [ ] After a peer merges, rebase on main; verify any squash captured the intended content by grepping
      the merged result, not by assumption.
- [ ] Distill candidates capture failures and inefficient behavior
      asynchronously; bounded synthesis runs at milestones, weekly, or on a
      recurrence/cost trigger.
