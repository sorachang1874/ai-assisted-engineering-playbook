# Adversarial Design Review Loops and Invariant Checklists

Distilled 2026-07-13 from a six-round cross-model design-review loop run on the sourcing-agent
repo (Track D agent-runtime design: Claude Fable 5 authored, GPT-5.6 reviewed through the
canonical read-only runner; three valid hash-bound artifacts + three extracted-reference
transcripts). This doc owns the *design-input* review loop; `08-review-and-delivery-checklists.md`
keeps gate operations, `13-operator-decisions-and-evidence-integrity.md` keeps evidence integrity.

## 1. The non-convergence dynamic (measured)

Findings per round: 24 → 16 → 17 → 6 → 5 → 11. Every round fixed layer N and the reviewer found
layer N+1 — because each fix *introduces new mechanisms* (a CAS, a grant record, a result slot)
that themselves lack fences, lifecycles, tenant keys. This is not reviewer noise: every round
caught at least one genuine defect, including author regressions (a tenant key silently dropped
during a rewrite) and real production-grade holes (simulated evidence able to become authoritative
state). The terminal state of an unmanaged loop is "the document equals the implementation."

Manage it with three levers:

1. **A design invariant checklist applied mechanism-by-mechanism before round one.** Post-hoc
   classification showed ~80+ findings across six rounds collapse into ~10 recurring invariant
   classes applied to newly introduced mechanisms: single-writer/aggregate ownership; tenancy keys
   in every row identity and CAS predicate; generation/physical fencing incl. ABA windows and
   *interactions with pinned physical constraints* (two commands sharing an idempotency-key
   unique constraint); lifecycle completeness incl. reverse transitions and timer ownership;
   late/partial results (quarantine, accepted-but-unconsumed windows, non-authorizing truncation);
   cost honesty (worst-case reservation, per-physical-call exposure rows with a
   possibly-sent state, reconciliation); physical identity binding (call id, response digest,
   effective config snapshot, pins persisted at each durable object's actual creation point);
   provenance/trust boundaries (model output never self-attests transport metadata; ingress
   cannot forge server-owned references); self-containment/cross-doc consistency (no "same as
   vN" references; shared contracts defined once); runtime/mode isolation (immutable
   namespace+provider-mode in every acceptance path; simulated evidence structurally unable to
   become live state).
2. **A mechanism × invariant matrix as a first-class design artifact**, cells filled by parallel
   verification agents (one per class), not by author self-assessment. In the measured run the
   first self-sweep intercepted 74 findings pre-review — including four blockers the author had
   introduced while fixing the previous round.
3. **Calibrated reviewer prompt + explicit termination rule.** Tell the reviewer: blockers are
   only factual errors, contract violations, unsound mechanisms, and contradictions; anything the
   implementation-batch protocol (scout / characterize-first / per-batch gate) will settle is an
   obligation — check the recorded obligation ledger before raising, cite instead of re-raise.
   Terminate when a round's blocking set is empty or consists only of recorded obligations; then
   the owner accepts the residual as an explicit exception and the findings convert into
   implementation-batch entry obligations. Without an owner-set stopping rule the loop runs
   forever, because a reviewer's standard legitimately rises to meet the document.

**The checklist itself must iterate.** Track the invariant-class distribution of each round's
findings; a class that keeps appearing means that column of the self-sweep is failing — fix the
checklist column before fixing the document. (Measured: round six exposed that the initial
nine-class checklist entirely lacked runtime/mode isolation, and that its fencing class did not
ask about shared unique-constraint interactions.)

## 2. Review-runner operations (portable lessons)

- **Give the reviewer a dedicated config home.** Desktop apps rewrite shared CLI config on
  launch (observed: ChatGPT Desktop downgraded top-level reasoning effort and set
  `service_tier = "default"`, which the runner's sentinel set treats as "not explicitly set" and
  fails closed). Fix: a bootstrap script materializes an isolated `CODEX_HOME` — everything
  symlinked back to the real home except `config.toml`, which is derived from the current shared
  config with a checked-in policy trio forced on top; the make target pins `CODEX_HOME` there.
  The script only reads the real home (verify by hashing the shared config before/after).
- **Dual CLI installs drift.** A PATH-resolved wrapper and a package-manager install can diverge
  (observed: a stale npm install with a missing vendored binary, only hit from non-interactive
  PATHs; also: `npm` on PATH belonged to nvm, so "global" installs silently repaired the wrong
  copy). Pin the executable the runner uses; verify with the minimal PATH the runner sees.
- **Fail-closed transcript validation vs. protocol drift.** New CLI versions spawn parallel
  sub-review threads and stop inlining turn items; a single-thread transcript verifier then
  rejects genuinely completed reviews as `invalid_transport`. The review *content* is still
  recoverable: extract `agentMessage` items from the captured event stream into an
  `*.extracted-reference.md` clearly labeled as non-evidence. Reference-quality input for the
  author; never gate evidence.
- **Size timeouts to the model tier.** A 420s default timed out an ultra-effort reviewer that
  legitimately needed ~15 minutes; several historical "transport failures" were really timeout
  misconfiguration. Make the timeout an explicit parameter and default it generously.

## 3. What the loop is for

Run it when a design introduces distributed/concurrent/paid/multi-owner semantics and the
implementation seat is the bottleneck (the review loop costs reviewer tokens, not implementer
time). Do not run it to completion on paper: after the checklist matrix is green and the blocking
set is obligations-only, the per-batch implementation gates are the cheaper place to settle the
remaining depth.
