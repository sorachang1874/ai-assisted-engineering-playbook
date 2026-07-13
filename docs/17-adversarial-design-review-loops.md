# Adversarial Design Review Loops and Invariant Checklists

Distilled 2026-07-13 from an eight-round cross-model design-review loop run to termination on the
sourcing-agent repo (Track D agent-runtime design: Claude Fable 5 authored, GPT-5.6 reviewed
through the canonical read-only runner; valid hash-bound artifacts + extracted-reference
transcripts). This doc owns the *design-input* review loop; `08-review-and-delivery-checklists.md`
keeps gate operations, `13-operator-decisions-and-evidence-integrity.md` keeps evidence integrity.

## 1. The non-convergence dynamic (measured to termination)

Findings per round, full run: **24 → 16 → 17 → 6 → 5 → 11 → 9 → 7**. Every round fixed layer N and
the reviewer found layer N+1 — because each fix *introduces new mechanisms* (a CAS, a grant
record, a result slot) that themselves lack fences, lifecycles, tenant keys. The conclusive
data point came in round eight: its top blockers were the state machine and lost-wakeup race of
`awaiting_budget` — the mechanism round seven's remediation had introduced. The self-reference
also never closes on the process side: fixes come *from* the matrix, and every fix makes the
matrix stale, which the next round correctly flags. **Prose has no fixpoint.** This is not
reviewer noise: every round caught at least one genuine defect, including author regressions
(a tenant key silently dropped during a rewrite) and real production-grade holes (simulated
evidence able to become authoritative state; two commands physically colliding on a shared
idempotency unique constraint). The terminal state of an unmanaged loop is "the document equals
the implementation" — and the terminal findings are precisely the ones that real storage plus
race tests settle in hours while prose iteration only spawns meta-findings about them.

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
   first self-sweep intercepted 74 findings pre-review; the regenerated 200-cell matrix caught
   four more author-introduced consistency blockers before round eight. **Calibrate expectations:
   the matrix's real, measured value is intercepting author self-harm before the reviewer sees
   it (it did so in two consecutive rounds) — it does not and cannot drive the reviewer's
   blocking set to zero, because "unsound mechanism" at ever-finer granularity is always findable
   in prose.** Regenerate the matrix after every revision or its stale cells become legitimate
   findings themselves; give obligations stable IDs so the reviewer can cite instead of re-raise.
3. **Calibrated reviewer prompt + explicit termination rule.** Tell the reviewer: blockers are
   only factual errors, contract violations, unsound mechanisms, and contradictions; anything the
   implementation-batch protocol (scout / characterize-first / per-batch gate) will settle is an
   obligation — check the recorded obligation ledger before raising, cite instead of re-raise.
   Terminate when a round's blocking set is empty or consists only of recorded obligations; then
   the owner accepts the residual as an explicit exception and the findings convert into
   implementation-batch entry obligations. **In the measured run the mechanical termination rule
   never fired in eight rounds even when supplied as a binding instruction — the reviewer always
   legitimately classified the newest mechanisms' gaps as new blockers. The only real terminal
   state observed is the owner-accepted exception.** Plan for that from round one: the loop's
   deliverable is not a GO verdict but a hardened design plus a findings-to-obligations ledger
   the implementation batches inherit. Without an owner-set stopping decision the loop runs
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
