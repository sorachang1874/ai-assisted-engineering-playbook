# Testing Strategy

## Testing Pyramid for Agentic Projects

Use multiple layers instead of one expensive all-purpose test:

- Unit tests: pure logic, reducers, validators, parsers.
- Contract preflights: schema, owner matrix, cross-endpoint parity, command registry.
- Integration tests: real database, fake providers, object store, queues.
- Browser smoke: core user flows against local backend.
- Scripted workflow tests: realistic end-to-end workflows with provider fakes.
- Live provider validation: small targeted samples only.
- Nightly/pre-release: long-chain stability, recovery, latency, and pressure.

## What Long Tests Should Not Do

Nightly tests should not discover:

- A field has two owners.
- A reader still uses a legacy fallback.
- A command type has no owner.
- Two endpoints expose different contract semantics.
- A fake provider response shape differs from live expectations.

Those belong in fast preflight.

## Production-Parity Harness

For workflow-heavy systems, build toward:

- Real database type used in production.
- Real object-store behavior or a compatible stub.
- Fake HTTP providers that implement webhook, poll, dataset download, retry, rate limit, and error semantics —
  **and expiry + duplicate-delivery semantics** (see "Hostile Fakes" below): shape parity alone leaves the
  time and repetition axes untested by construction.
- Browser runner for end-to-end UI smoke.
- Clean data per run.
- No shared mutable test state.

## Environment-Dependent Lanes Fail Closed

A lane whose tests need an external runtime — a real database, a container daemon, a message
broker — can silently skip that subject when the runtime is absent and still report green. In a
gating lane that green is not evidence (principle 40): a skip is a hidden fallback from
"asserted" to "not attempted" (principles 2 and 11). Make the dependency hard:

- **REQUIRE flags, set unconditionally in the lane command.** Each environment-guarded fixture
  honors a `REQUIRE_<DEP>=1` flag that converts its skip into a hard failure; the gating lane's
  invocation exports the flag for every segment, so no segment can degrade to skipping.
  Developer-local runs omit the flag and keep the polite skip — one fixture, two postures.
- **Zero-skip or pinned-count assertion.** The lane's last step asserts the skip count is zero,
  or that the collected-test count matches a pinned value. "All collected tests passed" means
  nothing when collection quietly shrank.
- **Mutation self-check, once per lane.** Break the dependency deliberately — point the lane at
  an unreachable database, or stop the daemon — and confirm the lane goes red rather than
  green-with-skips. Run it when wiring the flags and again after any fixture refactor: a
  fail-closed path nobody has ever seen fail is a belief, not a mechanism.
- **Report skips even where they are legal.** Non-gating lanes may skip, but the count is
  surfaced in the run summary the operator reads, never buried — skipped is a reportable
  outcome, not noise.

## A Dormant Lane Is Not Evidence — Green Carries a Date

Principle 43 fails a lane that runs but skips its subject; the limit case is the lane that
never runs at all. CI triggers bind to pushes: an unpushed working branch means the gating
lane has not executed a single one of the commits a "CI green" claim covers. One team
discovered its curated contract lane had been dormant for ten days while 500+ commits landed
locally — every "lane green" statement in that window described a run that predated all of
them, and nothing in the claim's wording distinguished it from a fresh verdict.

- **A green claim names its run.** Any signoff, handoff, or ledger sentence citing a lane
  carries the run's date and head commit; the consumer diffs those against the claim's date
  and the commits under claim. A run older than the change it vouches for is dormant
  evidence and fails closed as evidence — exactly as a mass-skip green does.
- **Local lane runs are the actual verification when development is local-first — record
  them as such.** The local execution of the same lane command (command, commit, date,
  literal result) is admissible evidence; borrowing the "CI green" label for it, or citing
  CI while only local runs happened, launders one evidence class into another.
- **Check dormancy cheaply in the preflight.** Compare the lane's last-run timestamp to the
  branch's last-commit timestamp; staleness beyond a threshold is a finding about the
  *evidence channel* itself, surfaced before any claim relies on it.

## A Static Guard Is a Derived Artifact — Pair It With a Ground-Truth Probe

A guard that asserts "X is never present" by scanning a checked-in surface *derives* its
verdict from that surface — and the derivation rots when the authority surface grows a new
source. One team's schema guard derived its expectations from the baseline schema file
alone; once migrations beyond the baseline became a second source of truth, the guard fired
false positives long after — the physical database was correct and the guard's derivation
was stale. The false alarm then seeded a wrong fix premise ("the constraints were never
created"), caught only by a probe (`27-deep-session-orchestration.md` §1).

- **Enumerate the guard's authority chain and scan all of it.** Baseline plus every
  migration, config plus every overlay — a derivation pinned to the original file silently
  freezes the authority surface at the day the guard was written.
- **Pair the static view with a physical probe.** A catalog parity test reads the live
  system's own catalog (indexes, constraints, schema metadata) and diffs it against the
  statically derived expectation, so the static and physical views cross-check each other.
  A disagreement is first a finding about the *derivation*, not automatically about the
  system.
- This is principle 21 pointed at guards: a guard is a consumer of a derived truth, and
  validated-against-the-wrong-copy applies to it exactly as to any generated artifact.

## Custom-Loader Harnesses Rot Silently

When tests load a shared module through a custom loader — a Node VM with a
hand-rolled `require`, a transpile shim, a bundler alias — the loader's
dependency map is part of the test contract. Adding an import to the shared
module is a breaking change to every harness that loads it, and it breaks at
module resolution, in harness initialization, with errors that look like
product failures. Twice in one repository, a heavily imported module
(`api.ts`) gained an import and every VM harness with a hand-rolled `require`
failed at load time; both times the first debugging minutes went into product
code that had never run.

- **One static-dependency block per harness, fail-fast.** Stubs for modules
  the tests must never exercise throw an explicit "harness stub: module X is
  not loadable in this harness" error; real contract modules load through the
  same compiled path the product uses. A new dependency is added in exactly
  one marker-delimited place, not discovered loader call site by loader call
  site.
- **Resolution errors must present as harness initialization failures**, not
  as product assertion failures. The first diagnostic question — did the
  subject even load? — should answer itself from the error text.
- **Repair one, sweep the class.** When a shared module's new dependency
  breaks one loader, search for every sibling harness with the same latent
  defect: the same repository held eight `api.ts`-loading harnesses, only one
  was broken, and the class was proven twice — the verify-the-class discipline
  of the classify-then-edit sweep (`07-multi-agent-parallel-work.md`).

## Setup Functions Must Leave the Environment Fully Usable

A setup/prepare function that provisions an ephemeral environment — a fresh
schema, container, or sandbox — must leave it fully usable: schema *and*
versioned migrations *and* seeds. Call sites written against the old contract
never learn about a new precondition. One repository's isolated-test-runtime
setup created a fresh PG schema but did not apply migrations; when a later
change made the seed path require authoritative tables, every fresh-schema run
failed at seeding — including the exact commands the testing playbook
documented, which had been silently broken.

- **Fix in the shared prepare function, not at call sites.** Creating the
  schema and applying migrations in one place repaired every caller at once;
  patching call sites would have left the next one broken.
- **Regression-assert the end state, not the steps:** a freshly provisioned
  environment is fully migrated, and the setup is idempotent — safe to run
  twice against the same target.
- **Documented but never executed is a decaying asset.** Any documented
  operational flow needs periodic execution or a cheap fresh-environment
  regression test; documented commands nobody runs are prose-only norms, and
  prose binds nobody (principle 28).

## Hostile Fakes and the Revisit Leg

A fake is an implicit claim about which properties of the real dependency matter, and CI's reward
function (deterministic, fast, always-valid) is the pointwise negation of reality's hostility (outputs
decay, responses lag, events repeat). Kind fakes are therefore systematic drift, not carelessness — and
any defect that needs wall-clock time greater than the pipeline's duration is invisible to every gate
unless the fake compresses time (principle 27).

- **Hostile by default:** fake-issued references expire (after first dereference, or a count/virtual-clock
  TTL — never wall-clock sleeps); every write is delivered twice; a scheduled call in the sequence fails.
  The escape hatch is an explicit KIND flag for debugging — opt-in hostility never gets turned on.
- **Deterministic, never sampled:** scheduled hostility (every event twice; call #3 fails), not random
  1-in-K — a random hostile leg becomes the flaky test that gets tolerated, recreating kindness one level up.
- **The scenario is the teeth.** A hostile fake is inert without a leg that makes it bite:
  - *revisit leg* — after all writes, expire every lease (`fake.expireAll()` at a session boundary), then
    re-read every persisted and displayed reference and assert zero blank/broken surfaces;
  - *repeat leg* — double-fire each mutating action the smoke already exercises; assert exactly one effect.
- **Append-only hostility dimensions** (expiry, duplication, latency/timeout, partial failure, ordering):
  every production incident traced to a kind fake adds its dimension — the class-level analogue of a
  regression test. Waivers carry an owner and reason and are audited by the independent reviewer
  (principle 14), never self-attested by the fake's author.

## Provider Testing

Provider tests should separate:

- Request construction.
- Remote submission.
- Poll/fetch.
- Item-level retry.
- Late result quarantine.
- Evidence/adjudication.
- Materialization.

Batch providers should expose stable item IDs, not rely only on array order.

## Artifact Tests

For agent-produced workflows, test the artifacts, not only the code path that
generates them.

Add tests for:

- required fields and schema version;
- invalid or stale inputs;
- overwrite protection;
- redaction and sensitive-output rejection;
- explicit boundary flags;
- fail-closed status derivation;
- snapshot drift between reviewed inputs and current sources;
- malformed numeric or enum config;
- generated reports, queues, handoffs, status summaries, and manifests.

If a malformed input crashes the script before it can write a blocked artifact,
the operator loses auditability. Prefer fail-closed output with issue counts
over unstructured exceptions for expected bad input.

## Characterization Tests for Structural Refactors

Before a structural refactor that is *supposed to preserve behavior* — extracting
a module, collapsing a dispatcher to a table, moving a tick/loop into a registry,
deleting a dead dual path — write a **golden characterization oracle** first and
freeze it:

- Pin the observable behavior the refactor must not change — call order, argument
  shapes, summary/return slots, skip lists, raised exceptions — as an explicit
  snapshot, not prose.
- **Run the oracle green on the pre-refactor code too** (against a parallel-worktree
  checkout of the baseline, not by flipping the shared working tree — principle 16).
  An oracle that only ever ran against the new code proves nothing about equivalence;
  its whole value is that it passed on the control and still passes after.
- Treat the oracle as a **hard gate, frozen for the duration of the refactor**: do
  not edit it to make the new code pass. If the new code disagrees, either the
  refactor changed behavior (stop), or the oracle was wrong (fix it deliberately,
  re-pin against the control, and note why).
- **Mutation-check the oracle once**: reorder a step, flip a gate, drop a summary
  field, and confirm it fails. An oracle that catches nothing is worse than none —
  it certifies drift as safe.
- **Route the oracle where the code actually runs.** If the logic still lives in
  the old module, an oracle that only imports the new module passes while the real
  path is unverified (the same-worktree blind spot, principle 14).

This is the structural-refactor analogue of the regression test (principle 16):
a regression test pins one fixed bug; a characterization oracle pins a whole
behavior, so a "pure move" cannot quietly become a behavior change.

### Byte-Equivalence Gates for Verbatim Moves

The characterization oracle proves behavior survived a move; it does not prove
the *verbatim* claim itself. Behavior-preserving hand-drift — a reworded
condition, a reordered guard, a "harmless" cleanup — passes every behavioral
test while silently forfeiting the byte-for-byte guarantee the review relied
on. When a refactor claims "moved verbatim", gate the claim mechanically:

- **AST-extract every moved function** from both the old location (at the
  pre-move revision) and the new one, so formatting and position noise drop
  out of the comparison.
- **Normalize both sides through an explicit allowed-substitution table** —
  only the renames the migration itself declares (e.g. a self-method call
  becoming a repository-method call). The table, like the expected residual
  set below, is a reviewed artifact — an allowlist in the sense of
  principle 15: a rewrite not on the table is a deviation, never a judgment
  call.
- **Byte-diff per function and compare residuals to a pre-declared expected
  set.** Acceptance is exact set equality with counts named: one
  domain-retirement batch accepted on "34 byte-identical + 3 disclosed
  adaptations + 0 unexplained". Any unexplained residual fails the gate — it
  is either an undeclared behavior change or undeclared scope, and every
  changed line must trace to a declared intent (principle 24).

"Looks identical" in review is appetite, not a gate; the mechanical diff is
what catches the hand-drift that slips into supposedly-verbatim ports.

### Determinism Checklist for Double-Run Equivalence

A double-run comparison — run the same script twice, byte-compare the outputs — is only as
strong as the nondeterminism you removed: any source you missed either fails the diff spuriously
or, worse, happens to match and certifies nothing. One write-path A/B comparison that
byte-compared five tables only became stable after closing all three of these:

- **Freeze the clock at every layer that reads it, not just the facade.** The entry point, the
  module under migration, and the DB adapter each read their own clock; freezing only the top
  layer left two live clocks, and the resulting timestamp drift diffed every row. The layer you
  froze is not necessarily the layer that runs — the same blind spot as same-worktree review
  (principle 14).
- **Pin time-derived decision fields far beyond the test horizon.** A lease or TTL expiry that
  sits near "now" can flip a branch between run 1 and run 2 — expired in one, live in the
  other — so the runs execute different code paths and the diff reports a phantom behavior change.
- **Reset ID sources explicitly; `TRUNCATE ... RESTART IDENTITY` is not enough.** Standalone
  sequences (dump-style DDL without `OWNED BY`) are not reset by `TRUNCATE`, so run 2 starts at a
  higher id and every id-bearing row differs. Issue an explicit `ALTER SEQUENCE ... RESTART`, or
  normalize ids to run-relative ordinals before comparing.

## Promotion Boundary Tests

Any artifact that can influence a downstream decision should carry negative
capability flags such as:

- external requests allowed;
- secret reads allowed;
- cache writes allowed;
- user-facing output allowed;
- publication allowed;
- scheduling allowed.

Tests should prove dangerous flags are ignored, rejected, or forced false until
the correct gate passes. A green parser test is not enough if a later summary
can accidentally reinterpret a planning artifact as execution evidence.

## Pre-Manual Tests

Before manual QA, run a pre-manual gate that checks:

- Core endpoints are coherent.
- Readiness and counts use one source of truth.
- No normal-path fallback was used.
- Recent workflow metrics are within known ranges.
- UI does not expose contract/debug wording to end users.
- Provider fakes match live response shape for the tested path — and live *hostility* (expiry,
  duplicate delivery) per "Hostile Fakes" above, or carry an owned, reviewer-audited waiver.
