# Finding Your Unknowns (Pre-Dispatch Discipline)

The framing and the technique vocabulary in this doc come from Thariq Shihipar's essay
*A Field Guide to Fable: Finding Your Unknowns*
(https://x.com/trq212/status/2073100352921215386), written from the perspective of one
engineer driving one strong model. This doc does not restate the essay; it welds the framework
onto the machinery this playbook maintains — because every technique in it has a landing point
this playbook owns: a brief section, a contract cell, a handoff field, a gate. Three of those
landing points are added by the same change that ships this doc (the brief's **Blindspots**
section, the handoff's **Deviations** field, and the decision queue with its card template) —
so the landing points below are facts of the repo on merge, not wishes (principle 28).

## The map is not the territory — and the gap is where agents guess

The **map** is the representation of the work you hand an agent: the prompt or task brief, the
skills, the context files. The **territory** is where the work actually has to happen: the
codebase, the runtime, the users, the real constraints.

> "The difference between the map and the territory is what I call unknowns."

That is the essay's definition, quoted; its claim is that with a strong model the bottleneck
moves to *you* — the quality of the work becomes limited by your ability to clarify the
model's unknowns. The operational reading this playbook adds on top: **an agent that hits an
unknown does not stop — it decides**, using its best guess at your intent. And the stronger
the model, the more territory it traverses per dispatch, so the more unknowns it crosses per
dispatch, and the more consequential each guess becomes.

Most of this playbook is gate machinery — contracts, preflights, reviews, hostile fakes:
instruments for catching a wrong guess *after* it has been made. This doc is the input side of
the same loop: **shrink the guess surface before dispatch.** It is the move of principle 8 —
pull problem discovery from the expensive end of the loop toward the cheap end — applied one
station earlier than design artifacts, to the brief itself. And it matters more with agents
than with human colleagues, because of the observation behind principle 28: **an AI implementer
replicates the map's gaps with perfect fidelity.** A human colleague fills a spec gap by asking
or by shared context; an agent fills it with a confident, well-formed, plausible decision —
exactly the kind of defect every snapshot gate is structurally worst at catching (principle 25).

## The four quadrants

Break any piece of work along known/unknown × known/unknown:

| Quadrant | What it is | Where the playbook lands it |
| --- | --- | --- |
| **Known knowns** | what you actually wrote in the brief | the brief's Goal/Context; frozen contracts |
| **Known unknowns** | questions you know are still open | open *decisions*: stop conditions in the brief, rows in the decision queue — never fanned out over |
| **Unknown knowns** | things so obvious to you that you never wrote them down, but you recognize them on sight | extracted by prototypes and interviews; converted to contract cells |
| **Unknown unknowns** | the questions you don't know to ask | blindspot passes before dispatch; cross-model review after (principle 14) |

Three consequences fall straight out of the grid:

- **Contract-first development is a machine for converting unknown knowns into known knowns.**
  The nine-cell owner matrix (principle 1) is a structured interrogation of the author: every
  cell you struggle to fill is an unknown made visible while it is still cheap. The verb
  contract's required actor model (principle 25) is the canonical example — "the user clicks
  once and sees the feedback" was an unknown known — obvious to every developer and written
  down by none — until first real-user contact proved that tests inherit the unwritten
  assumption. The fix was to make it a required spec field. That is the pattern in general:
  the cure for an unknown known is a form with a blank that will not stay blank.
- **A known unknown that only a human can resolve is a decision, and decisions are invisible
  work items by default.** On one audited project, a handful of zero-engineering product
  decisions sat unmade for two weeks, blocking contract freezes and two full work lanes, while
  engineering polished features — because no board tracks "waiting for a human yes/no" as work.
  Known unknowns of this kind go into an explicit decision queue with an owner, a deadline, and
  a pre-built decision card each — the decision-as-work-item discipline is principle 34; the
  card template is `templates/DECISION_CARD.template.md`, and the queue's landing point (where
  the rows live, and their required fields) is defined in
  `13-operator-decisions-and-evidence-integrity.md` § The Decision Queue. (That doc also owns
  the stricter, machine-verified regime for decision *files* that automation consumes — a
  different, harder contract than the queue.) The faster agents make implementation, the more
  throughput is governed by human decision latency.
- **Unknown unknowns are why unfrozen contracts must not be fanned out over** (the "when
  parallel agents hurt" list in `07-multi-agent-parallel-work.md`): parallel workers crossing
  the same unknown guess *differently*, and every branch looks done but does not integrate.

## The techniques, wired into the pipeline

Each technique below states when to use it, an example prompt (adapted from the essay), and —
the point of this doc — the playbook artifact it lands on.

### Before dispatch

**Blindspot pass.** Use when the work enters territory you have not personally worked: a new
module, an unfamiliar domain, inherited code. There you cannot even ask good questions — you do
not know what good looks like, what prior art exists, or which pits are marked.

> "I'm adding a new auth provider but I know nothing about this codebase's auth module. Do a
> blindspot pass: find the unknown unknowns — prior art, conventions, pitfalls — and help me
> write a better brief."

*Lands on:* the **Blindspots** section of the task brief
(`templates/AGENT_TASK_BRIEF.template.md`) — a required section, added to the template together
with this doc: prior art, this repo's conventions, known pitfalls. The author runs the pass
*before* the brief freezes and folds findings into Context, Constraints, and Stop Conditions.
A brief over territory the author genuinely knows must say so explicitly — "none — territory
known by author" — because the cure for an unknown known is a form with a blank that will not
stay blank, and that includes this one. A brief written over unworked territory without a pass
encodes the author's unknown unknowns as authoritative instruction — the worker will implement
the gaps faithfully.

**Brainstorm and prototype.** Use when unknown knowns dominate — work where you will only know
the standard when you see it (visual design, intervention points, UX shape). Discovering these
at implementation time is strictly more expensive than at prototype time.

> "Rough problem: users churn after onboarding. Search the codebase and brainstorm ten places
> we could intervene, from cheapest to most ambitious." — or — "Build one HTML page with four
> strongly divergent design directions so I can react to them."

*Lands on:* the window **before the contract freeze** (`02-contract-first-development.md`,
`07-multi-agent-parallel-work.md`). The freeze is the point at which an unexpressed preference
becomes expensive to honor; brainstorming also guards against framing the scope wrong before
any contract exists. Prototypes are probes, not products: they live in scratch/dev mode
(principle 6) and are exempt from gate machinery precisely because nothing consumes their
output — the moment something downstream does, principle 9 applies in full.

**Interview me.** Use after brainstorming, when ambiguity remains and you suspect your answers
would change the design.

> "Interview me, one question at a time, about anything ambiguous. Ask first the questions
> whose answers would change the architecture."

*Lands on:* the contract checklist. The interview is the conversational form of the owner
matrix — a good interviewer prompt asks exactly the cells you have not filled (owner? allowed
values? fallback? on-repeat behavior?). The architecture-questions-first ordering is
principle 19's front-loading applied to elicitation: spend the scarce round-trips where an
answer fans out.

**References as source code.** Use when you cannot describe what you want — no vocabulary for
it, or a full description would take longer than the work — but you can point at something
that has it. The best reference is working code, even in another language.

> "The Rust crate in `vendor/rate-limiter` implements exactly the retry/backoff behavior I
> want. Read it and reimplement the same semantics in our TypeScript client."

*Lands on:* the brief's Context section, as a first-class input class — the template's Context
section carries a "Reference implementations" line for exactly this. A reference
implementation is a spec that answers questions prose never poses — error taxonomy, edge
ordering, backoff jitter — which is to say it fills contract cells by example. This is the
constructive cousin of principle 18: ground the map in an artifact from the territory, not in
anyone's paraphrase of it.

**Plan with change-prone decisions first.** Use for any non-trivial implementation, once the
above have run dry.

> "Write an implementation plan that opens with the decisions I'm most likely to change:
> data-model changes, new type interfaces, anything user-facing. Put the mechanical refactors
> at the bottom; I trust you with those."

*Lands on:* the design gate and its review packet (`07-multi-agent-parallel-work.md`,
`02-contract-first-development.md` § Artifact-First Phase Model). Order the plan by decision
volatility, because the human's review attention is the scarce resource and a late change to a
data model fans out while a late change to a refactor does not. This is the same economics as
principle 19, applied to plan approval instead of gate rounds.

### During implementation

**Implementation notes with a Deviations section.** Use on every dispatch long enough to
survive first contact with the territory — which is to say, all of them. However much was
planned, unknown unknowns remain; the agent will meet an edge case that forces it off the plan.

> "Maintain `implementation-notes.md`. If an edge case forces you off the plan, take the
> conservative option, record why under 'Deviations', and continue."

*Lands on:* the handoff artifact — `07-multi-agent-parallel-work.md` § Handoff Artifact lists
**Deviations** beside Assumptions (its in-flight twin, added with this doc: empty means
writing "none", and each deviation carries a regression test pinning the chosen behavior,
proven non-vacuous per principle 16). Each deviation is an unknown discovered in the
territory: the plan said X, the code said no. Two rules give it teeth: a deviation that
changes *contract direction* is a stop condition, not a deviation — the agent halts and asks
(the brief's Stop Conditions section already says so); and a handoff with a non-empty
Deviations list requires human review, because deviations mark exactly the
specified-but-unstated corners where that review finds its highest-value defects.

### After implementation

**Pitch and explainer artifacts.** Use when shipping anything that needs another mind's
approval. A reviewer arrives holding your original unknowns plus some of their own; an expert
approver mostly wants proof that you found the unknowns *they* would have predicted.

> "Write the review packet for this change: open with the problems I already found and closed
> myself, the threat model, and what this review environment cannot exercise — then walk the
> diff."

*Lands on:* two existing artifacts. The **review packet**
(`templates/REVIEW_PACKET.template.md`) is the reviewer-facing explainer — the prompt above is
essentially that template spoken aloud; filling it section by section produces the pitch. The
practice of front-loading the already-closed-findings list, the threat model, and the
environment limits (`08-review-and-delivery-checklists.md`) is precisely "show the expert you
found their unknowns," which is what cuts gate round-trips (principle 19). The **decision
card** (`templates/DECISION_CARD.template.md`) is the approver-facing pitch: options, evidence,
a recommendation, and the single question to answer — so a human decision costs minutes, not
days, and the decision queue above actually drains.

**Quiz before merge.** Use when a long session has done more than you followed in real time.
Reading the diff yields shallow understanding, because much of the behavior lives in
pre-existing code paths the diff never shows.

> "Give me a report that helps me read and understand these changes — context, intuition, what
> exactly changed — with a quiz at the bottom that I must pass."

*Lands on:* the human merge gate. The async-topology rule is "the human merges after reading
the diff" (`14-async-multi-agent-collaboration.md`) — but reading is not understanding, and a
merge made without understanding is a rubber stamp with an audit trail, the same failure shape
`13-operator-decisions-and-evidence-integrity.md` exists to prevent in operator decisions.
The quiz converts the gate from *read* to *understood*. Mechanics, so this is copyable: the
implementing agent writes the quiz *and an answer key*; the human self-grades against it; the
result is a required field of the review packet / PR description — "Merge quiz: 4/5; failed
Q3 → tracked item #NN" — so a missing quiz is caught by the packet checklist, not by memory.
Merge only on a pass; a failed question is a discovered unknown: it converts to a tracked work
item (principle 10) before the merge proceeds, and gets landed like any other (below).

## Unknowns in multi-agent dispatch

The essay's frame is one human × one model. This playbook runs two multi-agent topologies —
fan-out (`07-multi-agent-parallel-work.md`) and long-lived async peers
(`14-async-multi-agent-collaboration.md`) — and in both, the map problem compounds, because
every dispatch is a re-projection:

- **A brief is a map of a map.** The human's intent projects onto the lead's map, which
  projects onto each worker's brief; unknowns can be introduced at every projection. So the
  brief carries its unknowns explicitly: known unknowns become Stop Conditions; territory the
  brief-author has not worked gets a blindspot pass before the freeze; and shared-seam unknown
  knowns are why producer and consumer briefs pin the exact same field names (the seam-drift
  failure mode in `07-multi-agent-parallel-work.md`).
- **Workers write deviations back to the ledger; they never silently re-route.** A worker's
  discovered unknown is information the lead paid for. In fan-out it travels in the handoff
  artifact; in the async topology it goes into the append-only coordination log — and if its
  resolution is normative (a contract nuance, an ownership fact), it is promoted to git
  (principle 22), because a deviation resolved only in one chat window is invisible to every
  agent that was not watching and to every future instance.
- **An unknown that invalidates the approach is a stop condition, not a deviation.** The
  essay's sharpest point is that some unknowns tell you the problem should be solved a
  different way entirely. In dispatch terms: that is a contract-direction change, and the
  worker halts and files the question rather than conservatively continuing down a wrong plan.
- **The reviewer's unknowns are why cross-model review works.** In quadrant terms: an
  author-family reviewer carries the author's map, so their unknown unknowns coincide with the
  author's, while a different model family carries a differently shaped map — and the
  source-of-truth audit goes one further, dropping map-to-map comparison to walk the territory
  before the gate does. See principles 14 and 18.

## Every discovered unknown gets an executable form

Per the postmortem corollary (principle 28), a lesson that stays prose is not implemented.
Finding an unknown is a lesson; land it where a machine can fail because of it:

| Unknown discovered… | Becomes | What fails if it doesn't |
| --- | --- | --- |
| in a blindspot pass or brainstorm, pre-dispatch | a brief Constraint/Stop Condition or a contract cell; scope changes become tracked work items (principle 10) | the design gate rejects a plan whose matrix has the blank |
| in an interview, at design time | a filled owner-matrix / verb-contract cell, or a recorded decision in the queue | contract preflight; the decision queue (`13-operator-decisions-and-evidence-integrity.md` § The Decision Queue) shows an open row missing owner or deadline |
| mid-flight, as a deviation | a Deviations entry plus a regression test pinning the chosen behavior (proven non-vacuous per principle 16) | handoff review flags a changed plan with an empty Deviations section; unpinned behavior drifts silently |
| by a reviewer | a failing-first test, lint, or fail-closed guard (principle 28); temporal ones become a hostility dimension in the fakes (principle 27) | the next same-class defect passes CI |
| at the merge quiz | a blocked merge; each failed question converts to a tracked work item (principle 10) — often a doc update (principle 7) or a naming/structure fix | the review-packet checklist rejects a packet missing its "Merge quiz" field, or carrying a failed question with no tracked item |
| in production | the postmortem corollary, as written | the incident recurs |

> **"Resolved in chat" is not resolved.** A chat window is a live channel, and the live channel
> is the bus, not the memory (principle 22). An unknown whose answer exists only in scrollback
> will be re-crossed — and re-guessed — by the next dispatch.

## Checklist

- [ ] Brief drafted over unfamiliar territory? Blindspot pass first; findings folded into
      Context, Constraints, and Stop Conditions before the brief freezes; known territory
      declared explicitly ("none — territory known by author"), never left blank.
- [ ] Known unknowns are either frozen decisions or Stop Conditions — never fanned out over.
- [ ] Zero-engineering decisions sit in an owned decision queue with decision cards
      (principle 34; `templates/DECISION_CARD.template.md`), not implicit on engineering
      boards.
- [ ] Taste-heavy work gets brainstorm/prototype probes before the contract freeze; probes stay
      in scratch mode and feed no consumer.
- [ ] Ambiguity remaining after brainstorm is interviewed out, architecture-changing questions
      first; answers land in contract cells.
- [ ] Reference implementations ride in the brief's Context when prose can't specify.
- [ ] Plans open with change-prone decisions; mechanical work sinks to the bottom.
- [ ] Every dispatch maintains implementation notes; deviations are recorded (with pinning
      regression tests) and human-reviewed when non-empty; contract-direction changes halt
      instead of deviating.
- [ ] Handoffs, review packets, and decision cards front-load the reader's unknowns.
- [ ] Long sessions end with a quiz; the score and any failed-question work items are recorded
      in the review packet; merge waits on a pass.
- [ ] Every discovered unknown lands in an executable form from the table above; none is left
      resolved-in-chat.
