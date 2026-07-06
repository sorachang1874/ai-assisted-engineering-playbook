# Residual Ledger

Every deliberate *no* — an accepted review residual, a deferred or frozen feature, an
automation declined, an architecture rejected — is a row here, not a memory (principle 30).
Memoryless reviewers and fresh sessions re-surface a true-but-accepted finding at full cost;
a ledger row lets the next review, audit, or gate round **diff against the decision instead of
relitigating it**. Principle 29's terminator feeds this file to the reviewer and requires every
finding classed as a residual to cite a row `id`.

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

## Preflight

A residual without a tripwire is prose (principle 28) — unbounded acceptance is forgetting with a
paper trail. Keep this file lintable and run the check with the other fast preflights
(principle 3):

```sh
# fail if any ledger row is missing its tripwire, or a `never` row its ratified-by/date
make lint-residual-ledger
```

Checks:

- Every row has a non-empty `tripwire` cell — **an entry missing it exits nonzero.**
- Every `status: never` row has non-empty `ratified-by` and `date`.
- Row ids are unique (gate rounds cite them by id; principle 29).
