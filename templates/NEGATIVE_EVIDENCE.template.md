# Negative Evidence

Every attempt that simply *failed* — a prototype that dead-ended, a model a bake-off excluded, a
fix that didn't fix — is a dated row here, not a memory (principle 39). Models are trained on
success-skewed data and under-report failure, so unless saving a failed attempt is the path of
least resistance the evidence evaporates and the next agent re-runs the experiment blind. This file
is **load-bearing, not archival**: it is instantiated beside the project's residual ledger
(`templates/RESIDUAL_LEDGER.template.md`), and the harness-change review in
`docs/08-review-and-delivery-checklists.md` § Cross-Model Gate Review diffs every new mechanism
proposal against it **before** a run is spent — a loop that re-proposes its own dead ends is the
self-inflicted version of a new agent re-proposing a rejected architecture (principle 38).

This owns the raw evidence *beneath* rulings. The siblings keep their territory: adjudicated
never-do decisions live in the residual ledger as `never` rows (principle 30); in-flight plan
departures live in the handoff's Deviations (`docs/15-finding-your-unknowns.md`); realized pitfalls
that already bit someone live in `docs/13-operator-decisions-and-evidence-integrity.md` § Pitfall
Log. When a negative here hardens into a decision never to retry, it **promotes** to the residual
ledger as a `never` row with a tripwire — until then it is evidence whose whole job is to stop the
next agent from re-running the experiment.

## Log

Record the mechanism at **three depths**, never the symptom (principle 39): two runs with identical
error logs can have entirely different root causes, and a symptom-level record misroutes the next
fix.

| id | what was tried | model/version/date | direct cause | causal state | abstract mechanism | why abandoned |
| --- | --- | --- | --- | --- | --- | --- |
| E-001 | `<the attempt>` | `<model X, version, YYYY-MM-DD>` | `<the surface error observed>` | `<the state that produced it>` | `<the root mechanism, one abstraction up>` | `<why it was dropped + recheck condition>` |

Example row:

| E-002 | structured tool-output streaming | `<model X>`, 2025-12 rev, 2026-06-17 | JSON truncated near 4k tokens | provider output cap hit mid-object | hard provider cap, not a schema fault | cap not configurable; recheck on next model rev |

## Records expire

Every record is **dated and version-bound — and therefore expires.** "X can't do Y" is true of
X-at-version-*v*-on-date-*d*, not of the name X. A capability negative read past its subject's
**next major release** is a prompt to *re-run* the experiment, not a license to obey the old
verdict — stale negative evidence is worse than none, because it silently excludes the option that
has since become the right one. One team seeded a model-selection survey with version numbers from
old notes and anchored the whole survey on superseded models, missing two newer releases until the
founder caught it.

## Preflight

Keep this file lintable and run the check with the other fast preflights (principle 3):

```sh
# fail if any row is missing its model/version/date or its abstract mechanism
make lint-negative-evidence
```

Checks:

- Every row has a non-empty `model/version/date` cell — an expiry needs a date to compute from.
- Every row records `direct cause`, `causal state`, and `abstract mechanism` (all three depths) —
  a symptom-only row exits nonzero.
- Row ids are unique (the handoff and harness-change review cite them by id).

The dispatch handoff (`docs/07-multi-agent-parallel-work.md` § Handoff Artifact) carries a required
`negative-evidence:` field — the attempts abandoned during that dispatch land here as rows, and the
handoff writes the literal word `none` when there were none; a **blank** fails the dispatch
preflight.
