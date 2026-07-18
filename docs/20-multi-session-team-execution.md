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
does not widen the packet locally.

Keep commits lane-local. Documentation and tests may be separate lanes when
their contracts are already frozen and their paths are disjoint; otherwise
they remain with the implementation owner or wait for the integration lane.

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

## Stale Packet Retirement

A packet becomes stale when its revalidation deadline passes, its base or
dependency is superseded, its hotspot turn changes, another diff enters its
write set, or the canonical contract changes. Time expiry alone does not
authorize takeover.

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
