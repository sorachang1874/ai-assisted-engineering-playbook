# Residual Ledger

Every deliberate *no* — an accepted review residual, a deferred or frozen feature, an
automation declined, an architecture rejected — is a row here, not a memory (principle 30).
Memoryless reviewers and fresh sessions re-surface a true-but-accepted finding at full cost;
a ledger row lets the next review, audit, or gate round **diff against the decision instead of
relitigating it**. Principle 29's terminator feeds this file to the reviewer and requires every
finding classed as a residual to cite a row `id`. Debt inherited rather than decided —
pre-existing type errors, known failures, skip inventories — is pinned here too
(§ Inherited-Debt Baselines).

## Ledger

| id | scope | what was accepted | why | correct fix | tripwire | owner | date | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | `<gate or artifact>` | `<the true finding not fixed>` | `<scoped to a threat/architecture model>` | `<what closing it would take>` | `<measurable condition that expires the acceptance>` | `<name>` | `<YYYY-MM-DD>` | accepted |

`status` values:

- `accepted` — a residual live under its tripwire.
- `deferred` / `frozen` — needs a **light-up and a kill condition**, both written into the
  tripwire cell (`re-activate when X; delete if unused 30 days past its window`). "Frozen"
  without conditions drifts back to keep.
- `closed` — the tripwire fired and the fix landed; keep the row for the audit trail.
- `never` — a ratified never-do (see below).

The tripwire is principle 1's deletion condition applied to a decision: the boundary of the
model the acceptance was scoped to (e.g. an accepted security residual expires at "more than one
semi-autonomous agent, or any external contributor"). Calibrate the tripwire itself with a metric
that says it was drawn wrong (e.g. "if post-hoc human vetoes of the advisory tier exceed 20%, the
boundary is wrong").

## Never-Do (ratified)

Machinery is nearly free for an agent to build and never free to own, so record with equal weight
what you will **never** build and why — otherwise every new agent re-proposes the rejected
architecture forever. Never-do items are ledger rows with `status: never`; they carry
`ratified-by` and `date`, and the tripwire cell states the evidence that would reopen the
question. The new-mechanism check in `08-review-and-delivery-checklists.md` § Cross-Model Gate
Review requires any mechanism proposal to diff against these rows **before** it is argued on the
merits.

| id | what was rejected | why | ratified-by | date | reopen-evidence (tripwire) |
| --- | --- | --- | --- | --- | --- |
| N-001 |  |  |  |  |  |

Grow automation the same way, by pre-committed tripwires recorded here: decide in advance what
evidence justifies the next tier ("LLM triage only after three real misroutes"; "a hard CI gate
only after the advisory digest is ignored twice").

## Inherited-Debt Baselines

Debt you inherit rather than accept — pre-existing type-checker errors, known test failures, an
old skip inventory — gets the same treatment as a residual: pinned, owned, and diffed instead of
remembered. One refactor team inherited 87 type-checker errors; rather than fix them all up front
or blanket-ignore them, they pinned the per-module count as a checked-in baseline and accepted
every batch against that pin. This is principle 16's known-failure budget made machine-checkable:
"the same set re-appearing unchanged" becomes a diff, not a recollection (a norm left as prose
is not implemented; principle 28).

- **One pinned fingerprint file per debt class**, checked in beside this ledger: the sorted
  known-failure list, the type/lint error count per module, the skip inventory. Sorted and
  deterministic, so the comparison is byte-stable.
- **Acceptance = identical against the pin**: byte-identical for list fingerprints,
  count-identical for per-module totals. Any other result is a finding, not noise.
- **The ratchet is only-down**: a decrease re-pins the baseline in the same change, so the win
  is banked and cannot silently regress; an increase fails the lane, with no override cell.
- **Every baseline is also a ledger row** — owner, date, and a tripwire that is the ratchet
  target or deadline ("module X at zero errors by <date>"; "budget under N before the next
  extraction batch").

## Preflight

A residual without a tripwire is prose (principle 28) — unbounded acceptance is forgetting with a
paper trail. Keep this file — and its companion fingerprint pins — lintable and run the check with the other fast preflights
(principle 3):

```sh
# fail if any ledger row is missing its tripwire, a `never` row its ratified-by/date,
# or an inherited-debt baseline moved above its pin
make lint-residual-ledger
```

Checks:

- Every row has a non-empty `tripwire` cell — **an entry missing it exits nonzero.**
- Every `status: never` row has non-empty `ratified-by` and `date`.
- Row ids are unique (gate rounds cite them by id; principle 29).
- Every inherited-debt baseline matches its pin or has moved only down — **an increase exits
  nonzero** (a decrease re-pins in the same change).
- Every cell that cites a test lane's green names the run's date and head commit; a cited run
  older than the change the row covers is **dormant evidence** and exits nonzero — an unpushed
  branch means CI never ran the claimed commits, and a local execution of the lane command is
  cited as what it is, never relabeled "CI green"
  (`docs/03-testing-strategy.md` § A Dormant Lane Is Not Evidence).
