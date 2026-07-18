# Multi-Session Team Execution

Subagents are useful for bounded work inside one conversation. Independent
Coding Agent sessions add a second kind of capacity: a human can keep several
long-lived tasks running, resume them separately, and choose different tools
or models per lane. Treat those sessions as a development team, not as extra
terminal tabs.

The unit of scheduling is a **session task packet**. A packet binds one
dependency-ready lane to one isolated branch/worktree, one exclusive write
set, one integration owner, and one evidence-producing handoff. Use
[`SESSION_TASK_PACKET.template.md`](../templates/SESSION_TASK_PACKET.template.md)
and validate an instantiated packet with:

```sh
python scripts/check_session_packet.py path/to/packet.md --ready
```

`--ready` fails when the packet has placeholders, lacks a 40-character pinned
base, has an unsatisfied dependency, omits validation/review/integration
fields, or leaves the stale-packet policy open.

## Team Roles

| Role | Owns | Must not do |
| --- | --- | --- |
| Integration lead | delivery graph, ready wave, packet issuance, hotspot order, integration, stale retirement | silently expand a worker's write set or treat a handoff as promotion approval |
| Session lane owner | one packet, its branch/worktree, declared paths, lane-local tests, immutable handoff | edit a dependency, another lane's path, central integration files, or live coordination board |
| Validation owner | shared affected-suite or realistic consumer path after lane integration | make every worker rerun the same broad suite |
| Independent reviewer | pinned read-only candidate review and scoped verdict | review mutable worktree bytes, self-certify, or block unrelated graph nodes |

One person or Agent may hold several roles over time, but not author and
independent reviewer for the same candidate.

## Packet Admission

A packet is `ready` only when all of the following are concrete:

1. **Pinned provenance:** repository and full base commit; every satisfied
   dependency names its commit or immutable evidence artifact.
2. **Isolated execution:** a unique branch and worktree path. Never point two
   writable sessions at the same working tree.
3. **Exclusive path lease:** exact read/write paths, lease owner, issue time,
   and revalidation deadline. The lease is permission to write only those
   paths, not ownership of the underlying product contract.
4. **Hotspot serialization:** each shared file/registry/schema names one
   hotspot, one current writer, the lane's writer position, and release
   evidence. A lane whose turn has not arrived stays blocked.
5. **Dependency wave:** graph run, lane id, prerequisites, and the downstream
   nodes this handoff can unblock. Session availability never overrides the
   graph.
6. **Evidence contract:** exact targeted commands and expected counts or
   invariants, shared validation owner, review mode, and protected promotion
   edges.
7. **Integration contract:** named integration owner, handoff path, expected
   commit shape, and merge/cherry-pick order.
8. **Staleness policy:** revalidate-after time plus concrete invalidators such
   as a superseded base, changed dependency, lost hotspot turn, or path
   overlap.

A blocked template may intentionally leave its base or dependency evidence
unset, but it must say why. It cannot pass `--ready` or be pasted into a new
session until the integration lead fills and validates it.

## Dispatch and Execution

The integration lead performs one sweep per event (handoff, review result,
hotspot release, dependency commit, or user request):

1. validate the durable delivery graph and print the ready wave;
2. issue one versioned packet per ready lane;
3. validate each packet with `--ready`;
4. create or assign its branch/worktree from the pinned base;
5. give the complete packet to a new Coding Agent session; and
6. record the claim in gitignored `.coord/`.

The lane owner verifies `HEAD == base_commit` before editing. If the session
discovers a new write path, contract direction, destructive action, live cost,
or hotspot collision, it stops and writes the question into the handoff. It
does not widen the packet locally. In a shared checkout it never stashes,
stages, reads, or formats another session's dirty files — the packet's
worktree preflight forbids adopting them — and a suspicious test failure is
attributed by running the exact failing node in a clean pinned worktree (the
baseline-attribution lane, `19-throughput-oriented-delivery.md` § Validation
Cost Belongs in the Graph), never by flipping the shared tree.

Keep commits lane-local. Documentation and tests may be separate lanes when
their contracts are already frozen and their paths are disjoint; otherwise
they remain with the implementation owner or wait for the integration lane.

## Interruption Safety

A session can die mid-task — quota wall, crash, expired model lease — and its
context dies with it. Two habits keep the lane resumable by a cold,
different-tool successor:

- Commit to the lane branch at every natural boundary, `wip:` commits
  included. Integration consumes commits or immutable handoffs, never dirty
  files, so early commits cost nothing; uncommitted bytes are attributable
  only by mtime forensics.
- Keep the lane's resume card current in its `.coord` status file: goal, base
  commit, touched paths, last validation command and result, state, next step.

The full recording protocol, the lead's dead-lane recovery sequence, and the
session-archaeology runbook for when records are missing are in
[`21-interruption-safe-handoff.md`](21-interruption-safe-handoff.md). A dead
session is not automatically a stale packet: recover card, branch, and
validation state before retiring anything.

## Dependency Waves and Review

Design waves around cut vertices:

```text
Wave 0: read-only inventory or decision packets with disjoint handoffs
Wave 1: one contract integrator freezes canonical schema/owner/equalities
Wave 2: disjoint implementation branches
Wave 3: serialized shared storage/registry/PG hotspot
Wave 4: shared validation and consumer E2E
Wave 5: pinned independent review, fixed-forward, then promotion/live
```

Review is an edge. A rebuildable non-live implementation may be committed and
reviewed while unrelated ready lanes continue. Only the named promotion,
paid/live, destructive, or milestone edge waits for the scope-matched verdict.
A review transport failure leaves that edge incomplete; it does not erase the
implementation evidence or authorize promotion.

## Integration and Handoff

The session handoff records full base/head commits, exact changed files,
commands with pass/fail/skip counts, deviations, review state, residuals,
negative evidence, and the next node unblocked. The integration lead then:

1. proves the base and dependencies still match;
2. compares actual diff paths with the packet lease;
3. reruns only the declared integration checks;
4. integrates in dependency and hotspot order;
5. launches the pinned review or records its existing artifact; and
6. updates the graph/board without rewriting the worker's handoff.

Integration by copied dirty files is forbidden. Consume a commit, a reviewed
contract packet, or an immutable handoff artifact.

Scope is part of the lease check: compare the landed diff's size and shape
with the packet's declared deliverable, not only its paths. An over-built lane
is pushed back to its bounded scope before integration, not integrated because
it is already written — one minimal SQL-fence lane grew to ~431 lines in
flight and was pushed back to +265 before its commit was consumed.

## Merging and Version Control for Lane Work

Lane branches are disposable delivery vehicles; the integration branch is the
only canonical line. A lane branch exists to carry one packet's commits from
one pinned base to one handoff. Once the integration owner consumes it, the
branch is deleted; work that lives only on a lane branch is invisible to the
graph, the board, and every other session.

The default integration mechanism is the cherry-pick of reviewed lane commits
onto the integration branch: never copied dirty files (forbidden above), and
never a merge of a lane branch carrying unrelated history — a merge drags the
lane's whole ancestry into the canonical line and makes a later bad change
unattributable to one packet. Integrate one lane at a time, in dependency and
hotspot order, and re-run the combined oracle — the affected suite over
everything integrated so far — after each pick, so a failure is charged to
exactly one lane while the culprit is obvious.

Choose the mechanism by boundary:

| Mechanism | Use when |
| --- | --- |
| cherry-pick | default: delivering reviewed lane commits into the integration branch |
| fast-forward merge | promoting a whole reviewed wave at once, when the integration branch has not diverged and linear history is preserved |
| pull request | the merge gate needs an external review surface — a human gate reviewing through GitHub (the doc-14 topology), a reviewer without local access, a fork, or a cross-project integration batch |
| rebase | only on a lane's own branch, before handoff, to refresh it onto a new pinned base |

Never rebase the integration branch itself: it is shared history, and
rewriting it invalidates every outstanding packet's pinned base and every
review artifact's pinned commit at once.

Before each pick, the integration owner verifies, in order:

1. the packet's pinned base and dependency evidence still match the graph;
2. lease compliance — the lane's diff touches only its leased write paths,
   with the scope check from § Integration and Handoff;
3. the packet's declared validation reruns green in the lane's own worktree —
   handoff text is a claim, not evidence; and only then
4. the pick lands and the combined oracle reruns on the integration branch.

### Branch Hygiene for Coordination and Documentation Repos

The same rules bind the repositories that hold plans, contracts, and docs —
this playbook included. One mainline (`main`); topic branches are short-lived
and merge back within days, not weeks; merged branches are deleted on both
sides. A branch that accumulates multiple unrelated topics, or outlives the
wave that created it, is itself an SSOT defect: the repository now holds
several candidate truths, and which one is current depends on which branch you
read. A documentation repo carrying a long-lived drafting branch beside
`main`, plus a stale feature branch still on the remote, has exactly this
shape; the fix is merge cadence, not better branch names.

Concurrent documentation edits by different agents are kept conflict-free by
routing and ownership — each lane owns different files or sections per the
documentation router (`18-documentation-routing-and-lifecycle.md`) — not by
long-lived parallel branches. Parallel branches are how a docs repo forks its
own truth.

### Merge Cadence

Integrate early, small, and often. Integration lag is a queue, not a badge:
every day a reviewed lane sits un-integrated, its pinned base rots toward the
`stale_if` invalidators and its review artifact drifts from the bytes it
certified, so revalidation cost grows. A pile of un-integrated lane branches
is work-in-progress inventory with branch names.

## Stale Packet Retirement

A packet becomes stale when its revalidation deadline passes, its base or
dependency is superseded, its hotspot turn changes, another diff enters its
write set, or the canonical contract changes. Time expiry alone does not
authorize takeover. Nor does a silent session: a lane that has gone quiet is
recovered first — card, branch, validation state — per
[`21-interruption-safe-handoff.md`](21-interruption-safe-handoff.md), because
its WIP commits may make it cheaply resumable from its own state.

The integration lead marks the old packet `retired` or `superseded`, records
the reason and replacement packet id, and issues a new packet from the new
pinned base. Do not edit a claimed packet in place: that makes the session's
instructions and evidence unverifiable. Completed packets and handoffs may be
archived after their commits and review artifacts are linked from durable
project docs; `.coord/` must not become a second backlog.

## Practical Width Rule

Open another Coding Agent session only when the graph has a ready node, its
write lease is disjoint or its hotspot turn is active, and the integration
owner has capacity to consume the handoff. Otherwise the fastest move is to
freeze the next cut vertex, clear a hotspot, or integrate completed work.
