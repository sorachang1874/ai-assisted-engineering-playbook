# Agent Task Brief

## Goal

What should be true when this task is complete?

## Non-Goals

What should not be changed?

## Context

Files, contracts, docs, and recent decisions the agent must read.

- Reference implementations (working code whose semantics to match, even in another language):

## Blindspots

Required (`docs/15-finding-your-unknowns.md`). If this brief covers territory the author has
personally worked, write `none — territory known by author` — never leave it blank, because the
cure for an unknown known is a form with a blank that will not stay blank. Otherwise run a
blindspot pass before this brief freezes and fold the findings into Context, Constraints, and
Stop Conditions:

- Prior art:
- This repo's conventions:
- Known pitfalls:

The six agent-failure-mode prompts — the canonical enumeration
(`docs/16-loops-and-model-composition.md` § The Agent's Own Failure Modes points here as its one
home). Answer each per task, or write why it does not apply:

1. Which external versions or capability claims does this task rest on, and where is each one's
   dated live check?
2. Which approach is non-negotiable here, where does the brief say so, and what would the tempting
   simpler substitute look like?
3. If this session dies mid-task, where do its notes, decisions, and partial results already live
   on disk?
4. What exact command and literal output will count as success — and what would a convincing false
   success look like?
5. What does a veteran of this domain know that no document states, and what stands in for that
   veteran here — an interview, a reference implementation?
6. Which single decision in this task deserves the most care, and is it routed to a human decision
   card or fenced as a Non-Goal?

## Affected Areas

- Modules:
- APIs:
- Tests:
- Docs:
- Runtime modes:

## Delivery Graph Coordinates

- Run id and checked-in graph path:
- Lane id and dependencies:
- Declared read paths:
- Declared write paths:
- Shared hotspot claims and writer order:
- Review lane and protected promotion lanes:
- Integration owner and handoff path:

If this is not part of a multi-lane run, write `single-lane — no delivery
graph`. Do not leave this section blank.

## Constraints

- 
- Closed world: edit only sites listed in `<table artifact>`; a site not in the table is
  reported as ambiguous in the handoff, never edited by inference.
- Do not edit paths outside this lane's declared delivery-graph writes. A newly
  discovered write or hotspot is a stop condition and must be added by the
  integration owner before work resumes.

## Validation

Run:

```sh

```

## Stop Conditions

Ask for human input if:

- A contract direction changes.
- A destructive migration is required.
- External credentials or live-cost decisions are needed.

If this brief launches a loop (goal-driven, scheduled, or event-driven —
`docs/16-loops-and-model-composition.md`, principle 36), also declare all three lines below; the
dispatch preflight (`docs/07-multi-agent-parallel-work.md`) fails a loop brief that leaves any of
them empty:

- Stop criterion (deterministic where one exists — tests pass, queue empty, PR merged; otherwise the verifiable completion criterion):
- Attempt / budget cap (max attempts, plus the token/spend ceiling):
- Trigger (`event: <source>` or `interval: <period>`, with a justification for the interval choice):

## Handoff Output

Report:

- Files changed
- Tests run
- Failures
- Residual risks
- Negative evidence (required — abandoned attempts land as rows in
  `templates/NEGATIVE_EVIDENCE.template.md`; write the literal word `none` if there were none, a
  blank fails the dispatch preflight; principle 39)
- Next step
- Delivery-graph lane unblocked by this handoff
- Distill candidates (failure or inefficiency mechanisms; `none` is valid)
