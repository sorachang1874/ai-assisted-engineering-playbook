# Shrink-Only Ratchets and Forensic Test Repair

Distilled 2026-07-22 from a production refactor continuation: a mid-life
codebase carried 81 stubborn type errors "held" only by memory, a 42k-line
un-runnable god test file, 213 test files whose reason-to-exist nobody could
trace, and a lane definition duplicated across two CI consumers with no drift
guard. Every one of these is the same disease — **debt that is tolerated but
not fenced** — and the same two mechanisms fixed all of them.

## 1. The shrink-only ratchet

A ratchet is a checked-in numeric or set-valued baseline plus a gate with
exactly three verdicts:

- **REGRESSION** — current measure exceeds the baseline: fail, fix the new debt.
- **RATCHET** — current measure is *below* the baseline but the committed
  baseline was not shrunk in the same change: fail, with the instruction to
  shrink it. Improvements must be captured, or they silently erode (we found a
  CI comment claiming 87 type errors while reality was 81 — six real fixes had
  landed with no artifact noticing).
- **IDENTITY** — the measurement configuration changed (tool version, config
  hash, file scope): fail, demanding an explicitly sanctioned re-baseline
  commit. Otherwise config drift launders itself into "progress".

Design rules learned the hard way:

- Key baselines on **stable identities** (file + error-code counts, file-name
  sets), never line numbers — hot files churn thousands of lines.
- Record the tool version and a hash of the measuring config inside the
  baseline artifact.
- Grandfather what exists, gate what changes. A ratchet that demands a
  big-bang cleanup on day one gets deleted by week two. One that only refuses
  NEW debt and forces captured improvements compounds forever.
- Ratchet everything of the same shape at once. In one day the same ~80-line
  gate pattern fenced: a type-error budget, a provenance-anchor grandfather
  set, a frozen god-file's test/line counts (shrink-until-deleted, then the
  gate guards against resurrection), and a single-source lane manifest parsed
  against both CI consumers.

## 2. Provenance, tombstones, and honest ignorance

Tests written as reactions to incidents outlive the memory of the incident.
Census before fixing: 6% of test files carried any traceable reason to exist;
every file written in the current month scored 100%. The contract that fixes
the flow without lying about the stock:

- New or materially-changed test modules MUST carry one machine-checkable
  anchor: an incident date, a ledger id, a contract-doc path, or a milestone
  id — enforced by an offline gate on the grandfathered-set complement.
- Deleting a grandfathered test requires a **tombstone row** (what it
  protected, why retired, superseded by what) in a routing index; the gate
  cross-checks deletions against tombstones.
- When origin is genuinely unknown, write `provenance unknown;
  characterization adopted <date>`. **Honest absence beats invented history**
  — bulk-backfilling rationales onto old tests launders ignorance into
  authority and is explicitly forbidden.

## 3. Forensic test repair (never rewrite assertions blind)

A failing legacy test is a *claim about a contract*, and the contract may have
legitimately moved. Repairing a stale suite is archaeology, not typing:

1. **Attribute first.** Prove the failure is pre-existing against a pinned
   baseline (worktree copy, not stash) before touching anything.
2. **Probe actuals.** Run the failing scenario and print what the system
   actually does now. Write assertions from measured behavior, then judge
   whether that behavior matches the ratified contract — two separate steps.
3. **Expect multiple mechanisms.** One "7 failing tests" ledger row dissolved
   into four distinct causes: literal fixture keys that should derive through
   the product's own helper; a fake test-double whose interface silently
   drifted off the real write path (its captured method was no longer called
   at all — migrate to the real store and assert on the durable surface);
   a paid-cost guard added after the test was written (the test must now
   carry the explicit authorization the guard demands — the guard is right,
   not the test); and a vocabulary evolution (a coarse status became
   provenance-bearing).
4. **Guard refusals are findings.** When a promotion/coverage guard rejects
   your migration, read its reasoning before overriding. In our case the
   guard's "no measurable improvement" verdict was CORRECT — the value was in
   a cache layer the metrics don't see, so the right move was a cache-merge,
   not a forced promotion. Never add an override path just to make a batch
   pass.
5. **Retire with tombstones, pin the future with flip-targets.** Tests that
   encode a never-landed design become tombstoned retirements (design intent
   preserved by commit hash), or explicit *flip-target pins*: tests that
   assert the CURRENT (wrong-but-live) contract, name the batch that will
   flip them, and fail loudly the moment that batch lands — self-scheduling
   regression coverage for planned migrations.

## 4. Cost-profile exploration before heavyweight commands

The companion operational rule (it saved this refactor twice in one day):
before running any command whose cost profile you have not measured, spend
one probe understanding what it actually does. A "promotion" CLI turned out
to be an unbounded cross-snapshot merge sweep — 75 minutes of re-materializing
stale history, merging poisoned sources, without ever performing the flip —
while the actual need (a guarded registry upsert + pointer write) was two
O(1) operations that a 60-line committed script executed in seconds, with a
dry-run mode that prints the guard's predicted verdict before writing
anything. If a tool's name says "do X" but its semantics say "do X across all
history", the name is not the contract; the probe is.
