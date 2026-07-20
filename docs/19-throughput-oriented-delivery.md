# Throughput-Oriented Delivery: Dependency Graphs, Coordination, and Distillation

Fast AI-assisted development is not the same as keeping every agent busy. The
useful target is shorter time from a product objective to a verified,
integrated capability. Unplanned fan-out often does the opposite: agents edit
the same hotspots, migration work starts before its partitions are understood,
reviews become global stops, and each session rediscovers the same context.

This chapter joins four practices that should be designed together:

1. a checked-in delivery dependency graph;
2. a local `.coord/` channel for live multi-session coordination;
3. review and validation lanes that block only their real dependents; and
4. periodic distillation that converts repeated failure *and inefficiency*
   mechanisms into executable project or playbook improvements.

The method applies to one lead with spawned workers, several long-lived
interactive sessions, and related repositories that will integrate later. The
transport differs; the dependency and ownership rules do not.

## Optimize the Critical Path, Not Agent Utilization

A lane is parallelizable only when all three statements are true:

- every dependency edge into it is satisfied;
- its write set is disjoint from every concurrently runnable lane, or an
  explicit hotspot serialization order exists; and
- it has an independently checkable deliverable and stop condition.

"Backend", "frontend", "tests", and "docs" are not automatically independent
lanes. They become independent only after the API, schema, owner, or product
decision they consume has frozen. Conversely, a pending review of one
rebuildable implementation does not make an unrelated module dependent on that
review.

The planning objective is to expose the real graph:

```text
product outcome
  -> decision / contract cut vertices
  -> disjoint implementation lanes
  -> lane-local validation
  -> scoped review
  -> fixed-forward repair, when needed
  -> integration and promotion
```

Measure queueing and rework on that path. A wide fan-out with many conflicts is
slower than three clean lanes whose outputs integrate once.

## Two Control Surfaces

Keep normative execution structure and live status separate.

| Surface | Location | Owner | Contains | Must not contain |
| --- | --- | --- | --- | --- |
| Durable delivery graph | Checked in under the owning module's `operations/` or `decisions/` directory | Integration lead only | dependencies, write sets, hotspots, validation, gate and promotion edges | heartbeats, transient ETA, chat summaries |
| Live coordination | local gitignored `.coord/` | each agent owns its status; lead owns board | claims, current status, commit, ETA, questions, graph pointer | the only copy of a contract or normative decision |

Use [`DELIVERY_GRAPH.template.json`](../templates/DELIVERY_GRAPH.template.json)
for the durable graph and validate it with:

```sh
python scripts/check_delivery_graph.py path/to/delivery-graph.json --ready
```

The command rejects unknown dependencies, cycles, runnable lanes whose
dependencies are incomplete, unregistered overlapping writes, invalid hotspot
serialization, and malformed review-to-promotion edges. `--ready` prints the
lanes whose dependencies are complete. The checked-in
[`delivery-graph.json`](../examples/delivery-graph.json) demonstrates an
asynchronous review running beside unrelated implementation.

Bootstrap the live channel from
[`COORD_README.template.md`](../templates/COORD_README.template.md) and
[`COORD_BOARD.template.md`](../templates/COORD_BOARD.template.md). The graph is
the plan; the board is an observation of its current execution. If they
disagree, stop scheduling from the board, update and commit the lead-owned
graph, then refresh the board.

For independent long-lived Coding Agent sessions, turn each ready graph lane
into a pinned, isolated, lease-bounded packet using
[`SESSION_TASK_PACKET.template.md`](../templates/SESSION_TASK_PACKET.template.md).
The issuance, stale-retirement, and integration protocol is in
[`20-multi-session-team-execution.md`](20-multi-session-team-execution.md).

## Top-Down Decomposition Protocol

Do this before implementation, not after scripted or end-to-end tests expose a
missing seam.

### 1. Name the product capability and its proof

State what a user or operator can do at the end, the surface through which they
do it, and the realistic path that proves it. A component count ("migrate 15
actions") is not a capability. A capability is closer to "an Agent can select,
simulate, execute, and inspect one bounded action through the served tool
surface."

### 2. Trace the vertical artifact chain

Walk backward from the consumer-visible result through read model, result
owner, runtime command, request schema, planner, and input. Mark every missing
owner, schema, serializer, served predicate, migration, and realistic test. This
prevents a broad scripted test from becoming the first inventory of incomplete
design.

### 3. Extract cut vertices

A contract, schema, shared type, owner decision, or provider policy used by
several lanes is a cut vertex. Give it one lead-owned decision lane and freeze
it before dependents run. Do not parallelize the decision itself by allowing
each consumer to invent a local answer.

### 4. Build lanes around deliverables, not activity

Each lane declares one owner, exact read/write paths, dependencies, hotspot
claims, a concrete deliverable, an exact validation command and expected
result, a deterministic stop condition, review mode, protected promotion
lanes, integration owner, and durable handoff.

Use exact repository-relative files or a subtree ending in `/**`; the validator
rejects other glob syntax because approximate overlap detection would create
false confidence.

Prefer a small vertical slice that reaches a real consumer over a wide
horizontal layer with no usable result. Split subsequent identical actions only
after the first path fixes the shared contract and generates a mechanical
migration table.

### 5. Mark shared hotspots before dispatch

Typical hotspots include owner matrices, central registries, storage
migrations, public schemas, generated inventories, root snapshots, and
integration tests. One lane owns each hotspot. Other lanes either read it or
depend on the owner lane and enter the recorded writer order later.

Two agents must not "coordinate carefully" while concurrently editing the same
file. That is an unmodelled serialization edge. Put the edge in the graph.

Generated and hash-chained artifacts are a distinct hotspot class. A fixture
bundle, a cross-project schema-pin file, or a self-hashing evidence chain has
no valid intermediate value: its content is a digest function of *all*
contributing lanes' outputs, so hotspot writer order cannot help — whichever
lane writes it mid-flight produces a value the next landing lane invalidates.
Model such artifacts as an explicit regeneration node owned by the integration
lead, depending on every contributing lane and running once after they land.
One orchestrator splitting a two-project remediation reserved fixture
regeneration, cross-project schema-pin updates, and the consumer preview
refresh for itself for exactly this reason — the self-hash chain must not be
concurrently corrupted; lanes shipped sources and inputs, the lead regenerated
once.

### 6. Add validation, review, repair, integration, and promotion nodes

Implementation is not terminal. Model what follows so the lead can start
independent work while a reviewer or expensive suite runs.

- Lane-local validation runs before handoff.
- A shared affected-suite lane waits for all relevant implementation lanes.
- A review lane consumes a pinned implementation artifact.
- A `NO-GO` creates a bounded fixed-forward lane for that scope.
- Promotion, live execution, destructive mutation, or milestone signoff waits
  for required review and repair nodes.
- Unrelated lanes with no path from that review continue.

### 7. Dispatch only the ready wave

Run the graph validator, then dispatch only the printed ready lanes. A worker
that discovers an unlisted write target or contract-direction change stops and
reports it; the lead changes the graph before redispatch. Do not silently
expand ownership because a nearby edit looks convenient.

## Related Products: Decouple Development, Contract the Convergence

Two repositories may serve one sourcing or mapping product while using
different discovery methods. Share the product objective, not the development
state.

During development each product keeps its own:

- repository/worktree and dirty-state boundary;
- module and contract owners;
- runtime, provider configuration, secrets boundary, and cost controls;
- tests, fixtures, evidence, commits, reviews, and release gates; and
- `.coord/` channel and delivery graph.

Do not let one project's agent edit the other's tree, import untracked files
from it, read its mutable runtime output as a normal dependency, or call its
unfinished service to make a local test pass. A shared dirty tree, implicit
relative-file dependency, or premature cross-project call turns independent
lanes into one unversioned distributed transaction.

Convergence happens through a separately owned, versioned boundary:

- **capability envelope:** capability id/version, supported modes and targets,
  request/result schema refs, evidence class, and owner;
- **request envelope:** stable intent, scope, tenant/requester, idempotency and
  policy pins;
- **result envelope:** schema version, status, artifacts, partial/failure
  semantics, and producer identity; and
- **evidence envelope:** exact producer commit/build, runtime mode, input and
  output digests, validation/review refs, and promotion boundary.

Freeze these envelope contracts in a neutral integration artifact. Each
project implements and tests its adapter independently against fixtures. Only
then create an **integration batch** pinned to exact commits from both
repositories. It owns cross-project composition tests, conflict resolution,
consumer-visible comparison, and a separate review. It does not amend either
project's historical evidence.

Use
[`CROSS_PROJECT_INTEGRATION_PACKET.template.md`](../templates/CROSS_PROJECT_INTEGRATION_PACKET.template.md)
to bind the candidates, envelope versions, independent adapter evidence,
integration batch, review, and promotion boundary.

The integration graph depends on the two project release candidates; neither
project graph depends on the integration work while its local capability is
still under construction. This preserves parallel speed without postponing the
eventual product contract.

## Review Is an Edge, Not a Global Stop

Use two review shapes.

### Blocking before execution

Design decisions, destructive or non-rebuildable mutation, paid/live external
execution, publication, and other irreversible steps keep a blocking edge. The
protected execution lane depends on the review lane.

### Asynchronous before promotion

For rebuildable non-live implementation, commit the bounded scope, launch a
pinned read-only review, and continue lanes that do not depend on its promotion.
The promotion/live lane depends on review; the rest of the graph does not. When
the result lands:

- a real finding becomes a fixed-forward lane naming the finding class and
  sibling surfaces;
- an already-fixed finding cites the fixing commit;
- an accepted residual cites its ledger row and tripwire; and
- a transport failure leaves review incomplete without erasing implementation
  evidence.

This avoids unsafe promotion and idle development. It makes review debt visible
as a graph edge instead of a narrative buried in a root TODO.

## Bulk Manipulation and Migration Protocol

Never begin a large sweep by serially editing or mutating the first items found.
The setup cost should produce a reusable execution plan:

1. **Inventory:** generate the closed set of files, symbols, rows, or owner
   keys. Record count and digest.
2. **Classify:** label each candidate by behavior and risk. An independent pass
   tries to refute every "safe" class.
3. **Generate the dispatch manifest:** workers consume the verified inventory;
   nobody retypes it. Unlisted sites are reported, not guessed.
4. **Plan partitions:** split by disjoint paths, owner keys, tenant ranges, or
   immutable identifiers. Record the union reconciliation rule.
5. **Pilot:** run a representative partition, including rollback or double-run
   equivalence where relevant, then adjust all remaining partitions.
6. **Fan out:** dispatch only disjoint partitions with per-partition validation
   and idempotent/restartable checkpoints.
7. **Reconcile:** prove completed partitions equal the original manifest by
   identifier, count, and digest; then run the real consumer-level test.
8. **Retire the bridge:** track compatibility or dual-write behavior to a
   deletion condition instead of normalizing it as permanent architecture.

If partitions share a transaction, mutable ordering, global counter, or common
writer, they are not parallel lanes. Improve the primitive first or serialize
the hotspot explicitly.

## Validation Cost Belongs in the Graph

Do not make every worker run every suite. Assign evidence by surface:

- worker lane: fastest contract and regression nodes for its deliverable;
- shared validation lane: affected cross-module suites after all inputs land;
- integration lane: consumer-level realistic payload or service path;
- promotion lane: expensive live, pressure, or manual checks only after gates.

Record command, duration, collected/pass/fail/skip counts, and expected
denominator. When a failure may be inherited, a separate baseline-attribution
lane runs the exact failing node in a clean pinned worktree. This prevents
multiple agents from debugging the same pre-existing failure and keeps costly
checks off unrelated lanes.

## Continuous Distillation Without Blocking Delivery

Distillation is not a postmortem reserved for crashes. Capture any repeated or
expensive mechanism that increased cycle time, review rounds, conflict, manual
work, context acquisition, or rework.

### Capture continuously

Any agent may append a candidate under `.coord/distill/` using
[`DISTILL_CANDIDATE.template.md`](../templates/DISTILL_CANDIDATE.template.md).
Useful inputs include session/terminal records, review artifacts, commit
topology, TODO/progress growth, routing gaps, coordination conflicts, idle waits,
duplicated suites, baseline comparisons, and bulk operations lacking a
generated inventory, pilot, or restart point.

Capture is asynchronous and must not edit an active lane's files. It records an
observation plus evidence; it does not interrupt delivery to debate policy.

### Synthesize on a bounded cadence

The integration lead schedules a distill lane:

- at each milestone or live-readiness boundary;
- weekly during active multi-agent development;
- after the same mechanism appears twice;
- after any avoidable review round, write conflict, repeated manual replay, or
  more than 30 minutes of attributable idle/rework; and
- before scaling a pilot method across modules, companies, providers, or data
  partitions.

The lane reads only the relevant evidence window and produces one of:

1. **Project-local enforcement:** a preflight, generator, router, template, or
   AGENTS rule prevents recurrence.
2. **Playbook generalization:** the mechanism is stack-independent and lands as
   a reusable method plus executable/template companion.
3. **No durable change:** evidence is anecdotal, already covered, or machinery
   costs more than measured waste; archive/discard it with the reason.

Do not turn raw session summaries into principles. A ratified distillation must
name observed behavior and evidence, causal mechanism, generalization boundary,
executable landing, maintenance cost, revisit/deletion condition, and adoption
path. This keeps the playbook from becoming another unbounded progress log.

## Lightweight Throughput Signals

Track only metrics that change scheduling decisions:

- critical-path elapsed time and ready-to-start wait;
- review wait blocking promotion versus review wait blocking nothing;
- hotspot conflicts or overlap rejections;
- fixed-forward commits and repeated finding classes per gate;
- duplicated validation wall time and baseline-attributed failures;
- context-routing time before the first useful edit; and
- manual bulk steps replaced by generated/restartable execution.

The goal is not maximum agent count. Add a lane or session when the graph has a
ready, owner-bounded node and an integration owner can consume its handoff.
Otherwise improve the plan or finish the current wave.

## Adoption Checklist

- [ ] Product capability and consumer-level proof are explicit.
- [ ] A checked-in graph names dependencies, writes, hotspots, validation,
      gates, promotion, and stop conditions.
- [ ] The graph validator passes and prints the intended ready wave.
- [ ] `.coord/` is gitignored; each agent owns one status file; lead owns board
      and graph.
- [ ] Shared contracts/hotspots have one writer and a merge order;
      generated/hash-chained artifacts are a lead-owned regeneration node
      after all contributing lanes, never a mid-flight write.
- [ ] Rebuildable reviews block promotion, not unrelated work; destructive,
      live, paid, or non-rebuildable work keeps a blocking review edge.
- [ ] Bulk work has generated inventory, verified classification, pilot,
      disjoint partitions, checkpoints, and union reconciliation.
- [ ] Related products keep independent trees/runtimes/tests/commits and meet
      only through versioned envelopes plus a pinned integration batch.
- [ ] Validation runs once at the narrowest useful lane, with separate baseline
      attribution for suspicious inherited failures.
- [ ] Distill candidates are captured asynchronously and synthesized on a
      milestone/weekly/mechanism trigger.
- [ ] A new session opens only for a ready node with bounded ownership and
      available integration capacity.
- [ ] Every independent Coding Agent session has a validated packet with a
      pinned base, unique branch/worktree, path lease, dependency evidence,
      hotspot turn, integration owner, and stale-retirement rule.
