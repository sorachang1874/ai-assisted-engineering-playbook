# Decision Card: <one-line ruling>

A queued human ruling — a product boundary, a quota value, a policy scope — is a work item, not
a hallway chat (principle 34). This card is pre-built so the human spends **minutes, not days**:
it is the approver-facing pitch (`docs/15-finding-your-unknowns.md`), and answering it drains one
row of the decision queue. One card = one ruling.

## The Single Question

State exactly one yes/no or pick-one question. If it splits in two, make two cards.

> <the single question to be answered>

## Options (with evidence)

| Option | Evidence for it | Cost / risk | Reversible? |
| --- | --- | --- | --- |
| A |  |  |  |
| B |  |  |  |

Evidence is why *this* option, not a preference — a benchmark, a cost line, a doc citation, a
production symptom. An option with no evidence column is a guess wearing a table.

## Recommendation

The card author's recommended option and the one-sentence reason. A card without a recommendation
pushes the whole analysis back onto the decider and defeats the point.

> Recommend: <option> — because <one sentence>.

## Deadline

- Decide by: `<YYYY-MM-DD>`
- Who decides: `<name/role>` — exactly one accountable decider.
- What this unblocks: `<contract freeze / work lane / ticket ids>`

## Timeout Default

If the deadline passes with no ruling, this fires automatically:

> <the default action, chosen so silence is safe — usually the reversible / closed-boundary
> option (principle 13)>

A timeout default is what stops a stalled queue from silently blocking engineering; it is the
decision-level analogue of a fail-closed boundary. A card whose safe default is "do nothing
irreversible" can sit past its deadline without bleeding.
