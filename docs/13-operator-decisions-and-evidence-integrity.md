# Operator Decisions and Evidence Integrity

This applies whenever a human decision changes how derived state is
interpreted: overriding a reviewed fact, approving an exception, suppressing
a field, promoting a candidate, or accepting a conflict resolution. The core
idea is that the decision itself must become a first-class artifact —
hand-authorable, independently reviewed, machine-verifiable, and bound to the
exact evidence generation it was made against.

These practices were distilled from a pipeline where display-name claims
conflicted with reviewed metadata facts and an operator had to decide, per
field, which value downstream consumers may prefer. The same shape recurs in
allowlist changes, manual data corrections, config promotions, and any
"human in the loop" approval that automation later consumes.

## Decision Files Are Contracts

Record decisions in a persistent file, not CLI flags, ticket comments, or
chat history. The file is the thing that gets reviewed, hashed, and audited.

Design rules for the decision schema:

- Hand-authorable: no machine-only fields. An operator cannot reasonably
  hand-compute a sha256, so do not put file digests inside decision rows.
  Copy-pasteable echoes are fine.
- Value binding: each row echoes the exact values it decides about, and the
  applier recomputes the content-hash reference from those echoes and
  requires it to match the upstream item. A decision can then never silently
  attach to a different item.
- Generation binding: each row echoes the upstream artifact's `generated_at`
  (copy-pasteable), and the applier requires equality. A regenerated
  upstream artifact — even one with identical content values — forces the
  operator to re-touch and re-review decisions.
- Closed decision enums, a required free-text reason with a hard length cap,
  a required operator identity (handle, not email, if your sensitive scan
  rejects `@`), and a required timestamp validated for format and for
  falling inside the window `[upstream generated_at, application time]`.
- Echoed ids (batch id, review id) are validated against both the CLI
  arguments and the upstream artifact, so a decision file from another run
  or review generation fails closed instead of joining cleanly.

## Per-Batch Independent Review, Machine-Verified

A design gate that approves decision *semantics* is not a review of any
*actual decision*: it runs before the decisions exist, and it cannot cover
re-decision batches created later. If applied decisions matter, require an
independent review of every decision batch:

- After the operator fills the decision file, an independent reviewer
  reviews that exact file and records an entry in a tracked review index.
- The entry must pin: the verdict, the batch id, the sha256 digest of the
  decision file, and every item paired with its approved decision.
- The applier machine-verifies the entry before applying anything: the
  anchor exists, the verdict line is present and is the approving verdict,
  the batch id and file digest appear literally, and every decision row has
  line-level pairing (below). Any post-review edit changes the digest and
  blocks the application until a fresh review exists.
- Dangerous decision classes (for example, preferring an unverified claim
  over a reviewed fact) additionally require a per-item review reference
  validated with the same content checks.

State the threat model honestly: these checks target drift and mistakes by
honest operators. A local editor who can forge the review index can forge
anything; that boundary belongs to repository access control, not to the
applier.

## Pairing Beats Containment

"The review entry mentions item X" is a much weaker check than "the review
entry pairs item X with decision Y on one line." Containment lets an entry
that approves one row's decision be read as approving a different decision
for another row, and lets an entry that only approves safe decisions
authorize a dangerous one. Machine checks should verify pairing — one line
containing both the item reference and the decision enum — and documents
should not claim a stronger review binding than the machine check enforces.

The same trap appears in anchor-style references generally: a check that a
referenced review *exists* authorizes nothing. At minimum, verify the
verdict, the scope marker, and the exact item reference inside the referenced
section. If the codebase already has a verdict-parsing helper, reuse its
conventions rather than inventing a second format.

## Digest Binding for Derived Artifacts

When an artifact is derived from several inputs, record the sha256 of every
input in the derived artifact (`source_digests`), then make consumers verify
the digests of the inputs they actually consume.

- Verify all of them. Partial digest verification creates silent staleness:
  if a consumer checks only one upstream digest, regenerating any *other*
  input pairs old derived state with new evidence undetected.
- Cross-check sibling outputs: if the summary claims N applied rows, verify
  the rows file exists and contains exactly N rows.
- Pick one canonical instance (a conventional default id that the consumer's
  default path reads); declare all other instances inert audit copies; and
  record supersession explicitly (`supersedes_*` lists) instead of letting
  contradictory parallel instances coexist with equal standing.
- Status-string cross-checks ("upstream says needs-review, derived artifact
  agrees") are not freshness checks. They survive regenerations that keep
  the same status. Use them in addition to digests, not instead.

## Consumers May Only Degrade

When a new artifact feeds a scoring, readiness, or status system, the new
consumer logic may only degrade or maintain the existing interpretation —
never promote it — unless promotion is itself the explicitly gated change.

- Cross-check any new score cap against every existing cap that binds in
  the same state. A "cap of 82" in a state where existing branches already
  cap at 80 is either dead text or a smuggled promotion, depending on which
  branch an implementer deletes later. Both are bugs; pin the cap at or
  below the binding one and say which existing branches remain in force.
- If the desired behavior requires modifying existing consumer functions
  (for example, replacing a pending action's text when the decision artifact
  is fresh), list those modifications explicitly in the design. "New loader
  plus new apply function" silently becoming "also rewrite two existing
  functions" is a classic scope dispute at implementation review.
- Write the consumer's apply logic as a total matrix over (upstream status x
  artifact status x integrity result). Every cell explicit, including the
  inconsistent corners: artifact present while upstream is absent, artifact
  contradicting an upstream that reports nothing to decide, and every
  integrity-check failure. Untotaled matrices force implementers to invent
  semantics under deadline.

## Every Status Must Be Reachable and Consumed

For every status in a new enum, demand two proofs: an input combination that
produces it, and a consumer branch that handles it. A status that no input
can produce, or that no consumer branches on, is a latent bug — delete it.

The common offender is a "nothing to do yet" status. Usually the honest
model is: not running the producer is the "not yet" state, the artifact's
absence is what consumers already handle, and a present-but-empty input is a
fail-closed error, not a third state.

## Honest Redaction Statements

Sensitive-output scanning is a best-effort net, and documents that describe
it must say what it actually catches and misses:

- A regex catches literal patterns: IP literals, URI schemes, credential
  keywords, long hex or base64 runs, domain-shaped strings. It cannot catch
  free-text properties like "no internal display names." Do not write "the
  scan forbids X" when X is not machine-detectable; write that X is
  forbidden by contract, constrained by vocabulary rules and length caps,
  and enforced by the mandatory human review.
- Free-text fields in operator artifacts (reasons, notes, identities) are
  the main leak vector. Cap their length, restrict their vocabulary by
  contract, scan them on read, and route them through the batch review.
- Do not quote scan patterns literally inside documents that the scan will
  later cover — the pattern matches its own description forever after.
  Reference patterns by location ("the credential keywords from the scan in
  <doc>") instead of inlining them.
- Validation claims in review packets must reproduce. "The scan returned
  no matches" must be the literal observed result of the recorded command,
  not a paraphrase of intent.

## Adversarial Pre-Gate Critique

Before submitting a design to an expensive independent review gate, run a
cheap adversarial critique pass with parallel lenses, each trying to refute
the documents rather than summarize them:

- fact-consistency: verify every concrete claim about the existing codebase
  against the actual sources (field names, enum values, derivations, line
  references, cited anchors, test counts);
- structure compliance: check the documents against their required templates
  (sections, labeled bullets, table columns, fixed rows);
- safety/boundary attack: hunt for paths where the design promotes evidence
  classes, leaks data, or lets a weak check authorize a strong action;
- design quality: hunt for unreachable statuses, untotaled matrices,
  unvalidated echo fields, missing format checks, and rework traps.

Findings should carry severity, exact location, refuting evidence
(file:line), and a suggested fix. After revising, run a separate
resolution-verification pass that checks every finding against the revised
text and hunts for problems the rewrite introduced.

Run the same critique shape again at implementation time, with the lenses
shifted to code: implementation-vs-spec conformance, consumer-integration
conformance, packet-claim reproduction (actually rerun the commands), and
test-coverage auditing (enumerate spec'd failure paths with no test, and
hunt for vacuous tests that block on a different issue than the one named).
Sensitive-scan heuristics in particular need fixture tests in both
directions: positives for each shape the scan claims to catch, and
negatives drawn from the artifact's own legitimate content (digests,
relative paths, timestamps, enum names) — the false-positive bugs hide in
the negatives.

In the originating case this caught 27 findings (5 blocking) before the
formal gate — all spec-level and fixable in text, which is exactly the
point: the formal reviewer's time is spent on judgment calls, not on
refutable claims.

## Pitfall Log

| Pitfall | Symptom | Practice that catches it |
| --- | --- | --- |
| Anchor-existence authorization | any unrelated review reference "authorizes" a dangerous action | verdict + scope + item-reference content checks; pairing beats containment |
| Substring lookup of authorization sections | a bare string-find resolves prefix anchors, mid-line mentions, or subheadings to the wrong section | line-anchored exact heading match, sliced to the next same-level heading |
| Containment check vacuous by identifier nesting | the batch id appears inside the anchor/section name itself, so "id mentioned in section" is always true | test containment checks with identifier-free section names; bind by digest, not by name |
| Refs spelled as filesystem locations | review references break when tools run with different working paths, or leak machine-local paths into artifacts | refs always name the canonical tracked path; CLI path flags only locate file content |
| Conditionally-skipped validation | a check guarded by "if upstream field parses" silently vanishes when the field is garbage | validate the precondition itself fail-closed before any check depends on it |
| Scanner heuristics vs legitimate content | hex/base64/address heuristics fire on the artifact's own digests, relative paths, and ISO timestamps — or get weakened until useless | negative fixtures from real artifact content; mask known-shape ids before scanning; scope blob heuristics to free-text fields |
| Twin fixtures, broken seam | producer tests and consumer tests each use hand-rolled fixtures of the shared artifact; both stay green while the real interface drifts | one cross-module test feeding real producer output into the real consumer |
| Noticed-but-tolerated defects | a loader records a malformed field as an issue yet still reports the artifact schema-valid; downstream state derivation ignores the issue list and promotes the artifact anyway | on promotion-eligible artifacts, every noticed defect must flow into the validity verdict itself, not only into a log or issue list; independent gate reviewers reproduce exactly this class |
| Default-path fallback reverts explicit inputs | rebuilding a derived chain with all-default arguments silently swaps in older input instances than the previous build used explicitly; presence flags stay true either way, so nothing looks wrong | derived summaries record the resolved path or digest of every input, not just presence; chain rebuilds replicate the prior build's explicit arguments; diff rebuilt chains at the metrics level, not only at the status level |
| Semantics-gate substituting for decision review | concrete operator decisions apply with zero review; re-decision batches bypass gates entirely | per-batch independent review, digest-pinned, machine-verified |
| Partial digest verification | regenerating an unchecked input silently pairs stale derived state with new evidence | consumers verify all recorded source digests |
| Score cap above existing caps | dead text now, smuggled promotion later | cross-check new caps against every cap binding in the same state |
| Unreachable status | enum value with no producer path and no consumer branch | reachability + consumption proof per status, or delete |
| Hidden modification of existing consumers | design lists only new code; behavior requires editing existing functions | name every existing function the integration modifies |
| Hand-computed hashes in operator files | operators cannot author the artifact; process gets bypassed | digests live in review entries and tool output; operators copy-paste echoes |
| Scan self-match | docs quoting the scan pattern match it forever | reference patterns by location, never inline |
| Same-family red-team to the asymptote, no source-of-truth audit | self-critique closes round after round of ever-rarer edge cases, yet the cross-model gate still returns NO-GO on a basic upstream-semantics miss (an unhandled default, a `!=`/set/wildcard spelling, a last-assignment reset, or a value the tool *requires* that the validator rejected) — sometimes a guard the self-critique itself "confirmed" was wrong | cap the same-family pre-pass at one or two rounds; before the gate, audit every external surface the artifact inspects or emits against its upstream reference doc (principle 18); prefer a canonical-shape allowlist so the audit is one schema-match question, not an open enumeration |
| Partial canonical-locking, or a root-derived canonical | a fail-closed checker deep-equals SOME deterministic sections of a generated artifact but semantically re-validates others — the gate keeps finding pass-but-leak mutations in whichever section isn't locked; or the "canonical" is derived from a mutable input (the `--root`, a source merge file) so drifting that input silently redefines what the deep-equal accepts | canonical-equality must cover EVERY deterministic section of a generated artifact, against a checker-OWNED canonical the generator imports (not a re-derivation from the input); anchor any derived canonical (e.g. an extracted domain set) to a pinned digest so input drift is rejected pending an explicit reviewed pin update; keep the semantic checks to PROVE the canonical is safe (principle 15) |
| Overstated scan claims | reviewed text asserts regex enforcement of non-detectable properties | honest redaction statements; contract + human review for the rest |
| Unreproducible validation claims | packet describes scan/test results that do not reproduce | record exact commands and literal observed output |
| In-place regeneration of cited evaluations | an adopted record cites a generated review file as "ready" evidence; re-running the evaluator with current rules overwrites it in place, so the adopted record contradicts its own cited evidence and the original verdict content is lost (fail direction may be safe, audit trail is not) | regenerated evaluations of the same subject write versioned instances with explicit supersession; adopted chains pin digests of cited evidence so any later mutation is detected instead of silently absorbed |
| Stale operator runbooks after CLI migration | long-lived runbook artifacts embed commands generated by older tool versions; a flag rename or semantics migration leaves an executable-looking but wrong runbook | generators that hand commands to operators recompute the canonical command set at handoff time and fail closed on byte-level drift; a re-run of the readiness evaluation demotes the stale runbook so pickers skip it |
| Chain segment regenerated, resume surface not | new downstream artifacts (queue, handoff) exist on disk but the documented resume entry point still walks the old pointer chain and dead-ends at superseded or contradicted artifacts | treat reachability-from-resume-docs as part of done: either ride the gated status refresh that re-points the chain, or explicitly record the new segment in the operator-facing report until that refresh lands |
| One cited line per gate round | each gate round fixes exactly the instance the reviewer named and re-gates, so one concept (e.g. an atomic-publish/cleanup requirement) is closed across three serial round-trips — introduce the cleanup, then learn it runs on only one failure path, then learn an early return skips it — and a canonical change (split/rename/added artifact) leaves un-swept ripple (stale files, doc inventories, counts) found rounds later | treat a finding as a class representative: fix every sibling path/surface with the same property and the full ripple of any canonical change in the SAME round, plus the adjacent class the gate hasn't asked about; front-load discovery with parallel self-review lenses over every surface the gate audits; batch the long tail into one consolidated pass + one confirming gate (principle 19) |
| Gate that does not guard its own control plane | a change edits the gate's own detector, sweep tool, or policy doc — weakening or obscuring the gate — without touching any path the gate protects, and routine "just tooling / just docs" maintenance walks through the hole | enumerate the gate's own files in its own protected set and prove it with a synthetic test (a change touching only the detector must trip the gate); declare code the source of truth over policy prose and check the prose against it (principle 31) |
| Untested wrap-up "hardening" sweep to safety tooling | a confidence-driven "while I'm at it" security touch-up at task close reintroduces a platform-specific bug that local checks never exercise — one commit fixed a BSD `mktemp` template-suffix trap (a suffix after the `X`s is taken literally, so the temp name is not random), and the very next "tighten temp-file permissions" sweep reintroduced the identical bug | hardening commits get feature-grade test discipline — if you cannot test the edit here, do not make it here (diff hygiene, principle 24); fail-closed construction (no parsable verdict ⇒ do-not-merge) bounds the damage when the rule is broken anyway (principle 31) |
