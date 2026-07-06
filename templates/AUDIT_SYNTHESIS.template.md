# Audit Synthesis: <surface audited>

A multi-lens audit structurally outputs "keep everything, improve everything" — every lens sees
some value, no lens is charged with the total cost of ownership, and LLM reviewers amplify the
bias because findings are almost always additive (principle 33). This synthesis is the
counterweight: one accountable role sums the maintenance tax across all the keeps and is rewarded
for **deletions and freezes**.

## Scope

- Surface / feature set audited:
- Lenses run:
- Date:

## Cuts and Freezes (the headline count)

| Verdict | Count | Items |
| --- | --- | --- |
| Cut (delete) |  |  |
| Freeze (defer with light-up + kill condition) |  |  |
| Keep |  |  |
| Net-new tickets proposed |  |  |

Frozen and deferred items become rows in `templates/RESIDUAL_LEDGER.template.md` (each with its
tripwire); cuts become deletion tickets.

## Summed Cost of Ownership

One line summing the maintenance tax across **all** the keeps — not a per-item note. This is the
number no single lens produces, which is the whole reason this role exists.

> Total cost-of-ownership of the keep set: <estimate + basis>

## Verdict-Reversal Log

The audit's highest-value output — it is what makes the audit auditable by the human who has to
decide. Two opposed charters (a deletion advocate vs a protect-the-core advocate) attack the same
synthesis; record every reversal with the **losing argument preserved**, and label an unresolved
disagreement with a recommendation. This is independence of *objective*, the incentive-side
complement of principle 14's independence of model family.

| Item | First verdict | Final verdict | Losing argument (preserved) | Decided by |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Cut-Critic Sign-Off

- Cut-critic (deletion advocate):
- Concurs with the cuts-and-freezes count above: `yes / no`
- If `no`: the disagreement is logged above as an unresolved reversal with a recommendation.

## Self-Check (the audit's own acceptance test)

> **Zero cuts plus net-new tickets, without the cut-critic's explicit concurrence, fails this
> audit.** "0 cuts, +N tickets" is a red flag about the audit itself, not a fact about the
> product (principle 33). If the box below is checked, do not ship the synthesis — run the opposed
> charter first.

- [ ] NOT (0 cuts AND net-new tickets > 0 AND cut-critic did not concur) — otherwise this audit
      fails its own acceptance and must re-run with a deletion advocate chartered against a
      protect-the-core advocate.
