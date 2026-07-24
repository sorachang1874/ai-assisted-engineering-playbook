# Deep-Session Orchestration: Fresh-Context Fleets, Probe-Chain Forensics, and Shadow-Slice Flips

Distilled 2026-07-23 (third backflow batch, same refactor continuation as
docs 25–26): how one deep orchestrating session kept landing green batches by
refusing to do the remaining work itself — dispatching each batch to a
fresh-context agent behind a mechanism dossier, proving a negative per layer
before opening any bug row, and flipping a deterministic rule ladder to a
model stage without ever betting the flip on the model's behavior.

## 1. The orchestrator's context depth is a dispatch signal

Doc 22 §1 engineered the review channel against mid-turn compaction; the same
failure hits the implementation channel from the other side. Hours into a
forensic session, the orchestrating context holds exactly what a fresh agent
lacks — probe-proven mechanism knowledge — while losing exactly what a fresh
agent has: the headroom to edit carefully. Both naive answers fail: keep
working in the deep context and edit quality decays toward compaction;
delegate with a thin prompt and the worker re-derives or guesses the
mechanism. The working answer is an asymmetric split — the deep context
writes a **mechanism dossier**, a fresh context executes it (principle 44):

- **Probe-proven facts, labeled as such.** Not summaries of beliefs — facts
  with the probe that proved each one, so the worker can re-run the probe
  instead of re-trusting the prose.
- **Hard rules with reasons.** What must not be touched and why — the "why"
  is what lets a fresh context generalize the rule to the case the dossier
  didn't anticipate.
- **Exact validation commands, copy-paste runnable, with expected literal
  output** — the same property doc 22 demands of review scope pins.
- **An honest-blocker escape hatch.** The brief pre-authorizes
  stop-with-reproduced-evidence as a *successful* outcome. Without it, a
  stuck fresh context invents workarounds precisely because it lacks the
  depth to know they are wrong.
- **License to disprove the premise.** Every premise is labeled
  `probe-proven` or `assumed`, and overturning an assumed premise with
  evidence is explicitly in scope. Real case: a fix brief premised on "the
  guard fires because the constraints were never created"; the worker's first
  probe showed the constraints existed and the *guard's derivation* was stale
  (§4 below) — the license converted a wrong compliant fix into a correct
  one-line derivation fix. This is principle 40's overturning rule granted
  upfront to implementation lanes, and the affirmative twin of the
  premise-conflict stop-and-ask in doc 24.

Six consecutive batches ran this way at the deep end of one session — each
green on its first gate, several overturning a caller premise — while the
orchestrator spent its remaining context on what only it could do: cross-batch
consistency, gate verdicts, and the next dossier. The orchestrator reviews
handoffs and gates, not diffs.

## 2. Probe-chain forensics: prove the negative before you patch

Principle 16 attributes a failure before you own it; doc 25 §3 probes actuals
before rewriting assertions. This is the layer for live-system bugs whose
mechanism is unknown: a chain of narrow probes, each of which **proves a
negative** before anything is touched.

- **One probe, one layer, one question.** A payload spy, then a function-call
  spy, then a status-write spy — each answers only "does this layer run with
  this data?", and the answer "never" eliminates a stratum for good. A wide
  probe that watches everything proves nothing; ten narrow negatives triage a
  ten-case failure inventory into three mechanism families in one pass.
- **Invariance proofs before a ledger row opens.** Before recording a
  mechanism, prove the failure is invariant under the suspected causes:
  stash-cycle the candidate change and re-run (failure persists with the
  change absent), and re-run in a pinned-commit worktree (failure predates
  the suspect commit — principle 16's parallel-worktree rule, not a working
  tree flip). A row opened on an unproven mechanism sends the fix agent down
  the wrong stratum with confidence.
- **The ledger row records the probe chain, not the symptom.** Principle 39's
  three-depth rule applied to live bugs: the row carries which probes ran,
  which negatives each proved, and the surviving mechanism — so a fix agent
  (dispatched per §1) starts from mechanism, and the dossier's "probe-proven"
  labels are literally citations into the row. A symptom-only row re-runs the
  entire forensics at full cost.

## 3. The shadow-slice ladder: flipping a rule ladder to a model stage

Doc 26 moved code out of a monolith without betting on reading comprehension;
this ladder replaces a deterministic rule ladder with a model stage without
betting on the model. Same doctrine, new subject: characterization oracle
first, rulings second, additive slices third, the flip last.

1. **S1 — exact-version contract and validator battery.** Pin the model
   output contract (doc 10) at an exact version, and write one validator per
   old rule, each carrying that rule's characterization pin — the rule ladder
   survives as machine checks before the model exists. The battery is the
   oracle of this migration; like doc 26's, it is never edited to make a
   later slice pass.
2. **S2 — the model surface returns RAW payloads.** No self-validation, no
   repair, no clamping inside the model stage: validation stays
   single-sourced in S1 (principle 15's one-canonical rule — two validators
   drift, and a self-repairing model surface hides exactly the drift the
   battery exists to catch).
3. **S3 — shadow integration with a byte-identity regression.** The model
   stage runs beside the rules in production paths, observed but never
   steering: a regression asserts dispatch output is byte-identical with
   shadow on and shadow off. This is doc 26's byte-identical oracle applied
   to a runtime flip — the shadow may disagree, log, and accumulate evidence;
   it may not influence.
4. **S4 — durable identity, backward-compatible.** Extend the durable records
   so shadow outputs are attributable (which stage produced what, under which
   contract version) without breaking old readers — the audit surface for the
   flip decision must exist before the flip.
5. **S5 — the flip, last, gated, pre-ratified.** Flip only behind an
   independent-review GO, and demote goldens to validators only under a
   demotion ruling ratified *before* the flip — so nobody relaxes the oracle
   mid-flip to make the model pass. A flip whose acceptance criteria are
   negotiated while the model is failing them is not a gate.

Each slice lands as its own reviewed batch — in the source case, each was a
fresh-context dispatch from §1, green-gated against the S1 battery plus the
surrounding suites.

## 4. Two evidence-rot mechanisms the session surfaced

Both closed as bounded fixes elsewhere in this playbook; recorded here because
the deep session is where they bite:

- **A static guard is itself a derived artifact.** The stale-derivation false
  positive behind §1's overturned premise: the guard derived its expectations
  from a baseline schema file while migrations had become a second authority
  source. The general fix — scan the full authority chain, and pair every
  static derivation with a physical ground-truth probe — is in
  `03-testing-strategy.md` § A Static Guard Is a Derived Artifact.
- **A dormant lane is not evidence.** An unpushed branch means CI never ran a
  single commit under the claim; "CI green" needs a freshness check (run date
  and head commit vs the claim), and local lane executions are the actual
  verification when development is local-first — see `03-testing-strategy.md`
  § A Dormant Lane Is Not Evidence and the ledger preflight clause in
  `templates/RESIDUAL_LEDGER.template.md`.
