# Loops and Model Composition

The operational content in this doc comes from three 2026 sources, gratefully: the **Claude Code
loop guides** (Anthropic, 2026-07 — full paths in `references.md`), which classify agent loops into
four types by what the human still supplies; **Anthropic's managed-agents cost-composition
material** (the advisor/orchestrator documentation and the cookbook notebook `claude-cookbooks` →
`managed_agents/CMA_plan_big_execute_small.ipynb`); and **Lilian Weng's harness essay**
(2026-07-04 — `references.md`), which treats the harness as code an agent can improve — and marks
where that loop must stop. This doc does not summarize them; it welds their content onto the
machinery this playbook already maintains. The siblings keep their territory:
`07-multi-agent-parallel-work.md` owns fan-out roles and the dispatch preflight,
`08-review-and-delivery-checklists.md` owns gate operations,
`14-async-multi-agent-collaboration.md` owns the async-peer topology and the two-layer memory,
`15-finding-your-unknowns.md` owns pre-dispatch unknowns, and principles 29–35 own gate
termination, ledgers, gate self-protection, retro-validation, audit accounting, decision queues,
and per-lane model fallback. What was unowned — and is claimed here — is the **loop itself**: how
much of it you hand over and when, how a loop that is *not* a review gate terminates, how models of
different cost compose inside one task, and what a self-improving harness must never reach.

## The Delegation Ladder

The four loop types in the loop guides differ not by what the agent does but by **what the human
has handed over**. Read in order, they form a ladder — and the order of hand-over is fixed: first
the verification steps, then the stop condition, then the trigger, and only last the prompt itself.

| Rung | Loop type | What you have handed over (cumulative) | What still requires you | Terminates on | Playbook wiring |
| --- | --- | --- | --- | --- | --- |
| 1 | **Turn-based** (interactive) | execution of the steps inside one turn | verification, stop, trigger, prompt — every turn | you end the turn | ordinary dispatch; the per-task `verify:` (`14-async-multi-agent-collaboration.md`) runs under your eyes |
| 2 | **Goal-based** | + the verification loop — the agent runs the checks itself | the goal, the attempt cap, the launch | a verifiable criterion or the cap, whichever first | the `verify:` line and the DoD evidence gate *are* the criterion; doc 14's board row gains an `expected-done` column (this change) |
| 3 | **Time-based** (routine) | + the trigger — a schedule starts it without you | the standing prompt; the interval choice | each run self-terminates; the routine carries a `revisit_when` date — the same dated-review convention as `templates/MODEL_ROUTING.template.yaml` | scheduled sweep; interval matched to the object's change rate (below) |
| 4 | **Proactive** (event-driven) | + the occasion — an event selects and parameterizes the run | the standing policy, and the tripwires that grow it | silent when empty | event-driven control plane; the poll retires (below) |

- **Trust is earned rung by rung, never granted upfront.** Climb a rung only once the level below
  can be verified *without you* — and pre-declare the metric threshold that unlocks the next rung,
  so escalation of autonomy is a recorded decision, not drift. This is principle 30's
  pre-committed-tripwire discipline applied to autonomy itself. One team climbed exactly this
  ladder for its coordination sweep — manual lead sweep, then a script, then event-driven triage on
  issue-opened events — with the next two rungs (LLM triage, headless owner agents) written down in
  advance as ledger tripwires on misroute counts and veto rates, not taken on enthusiasm.
- **Start at rung 1–2, and climb on a countable record, not a feeling.** A new loop defaults to
  rung 1; it may launch at rung 2 when its `verify:` criterion is already deterministic; rungs 3–4
  are never starting points. "Verifiable without you" has an operational default (repo-overridable,
  in writing): **three consecutive runs in which the human reviewer corrected nothing and the stop
  condition — not the cap, not the human — ended the run.** The hold at the current rung is a
  residual-ledger row whose tripwire is the unlock metric (principle 30); the climb closes it with
  a dated **grant row** — `date · rung N→N+1 · metric observed · evidence link` — appended to the
  same ledger, so an auditor can re-walk every escalation after the fact.
- **Hand over verification first and the prompt last.** The common failure is the reverse: a
  standing prompt fires on a schedule while no one has ever handed over — or even written down —
  the verification steps that would tell anyone whether its output is right. A rung-4 loop whose
  rung-2 machinery was never built is unsupervised in the precise sense: nothing can fail because
  of it (principle 28). The grant rows above are how this ordering is audited: each rung's grant
  row must predate the one above it.
- **Match the interval to the watched object's change rate — and prefer events to time.** A routine
  that polls faster than the object changes burns budget re-observing an unchanged world (loop
  guide). Where the platform offers events — webhooks, CI triggers, issue hooks — replace the poll
  entirely: as one team found when it retired a 20-minute polling sweep for event-driven triage,
  the event-driven control plane also survives the death of whatever local session used to run the
  poll. Its remaining daily digest runs daily because its objects (stale issues, open PRs) change
  on that timescale — and is silent when empty.

## Loop Hygiene

Principle 29 gives *review gates* their terminator. Most loops are not review gates — generation
and retry loops, polish loops, self-iteration with no reviewer — and they need the same discipline,
declared before launch, because a loop without a declared exit runs until token exhaustion or,
worse, drifts silently. This section extends principle 29 to them; for review rounds themselves,
apply 29 and `08-review-and-delivery-checklists.md` § Cross-Model Gate Review unchanged.

- **Every loop declares a stop condition and an attempt cap before it starts.** Deterministic
  criteria — tests green, score threshold, queue empty, PR merged — outperform "the model judges it
  good enough" (loop guide: "reach Lighthouse ≥ 90 or stop after 5 tries"). Executable form: the
  brief's existing `## Stop Conditions` section gains three lintable lines — stop criterion
  (deterministic where one exists), attempt/budget cap, trigger (event or interval, with
  justification); the board row's `verify:` is the criterion; and the board row schema in
  `14-async-multi-agent-collaboration.md` gains an `expected-done` column — task-id | owner |
  status | branch/PR | verify | expected-done | note — so a stalled loop is sweep-visible rather
  than quietly dead.
- **Budget is part of the loop contract.** Declare the token/spend cap before launch — it is one of
  the three Stop Conditions lines above — and measure real usage in the pilot slice (next bullet)
  before committing the full run. A standing live-usage meter is deliberately *not* required yet:
  no budget-overrun incident has earned that norm, and when one does, principle 28 says it lands as
  a lint, not as a sentence here.
- **Pilot before scale.** Dynamic workflows can spawn dozens to hundreds of agents; a full-width
  launch risks losing the entire run to a constraint a small slice would have surfaced for pennies
  (loop guide). Run a representative fraction first, measure usage and stall points, and fold the
  findings — per-agent budgets, fallback rules — into the full run's configuration. Principle 32
  already owns the pilot for *gates* (retro-validation); this is the pilot for *fan-outs*: the
  fleet-zeroing incident behind principle 35 was also a pilot failure — a one-lane slice would have
  hit the quota ceiling cheaply and forced the fallback design before the expensive run. Executable
  form: the Dispatch Preflight (`07-multi-agent-parallel-work.md`) gains a line with a hard
  default — a fan-out of more than 5 agents, or a projected spend above $50 (both thresholds
  repo-configurable), asserts that a pilot slice ran — and the dispatch log entry carries a
  required pilot-findings field: what the pilot changed in the full run's configuration.
- **A partially failed fan-out resumes; it never reruns survivors.** Give every fan-out a run id
  at dispatch and land each agent's output in files keyed by it — the concrete payoff of the
  lands-in-files rule that closes this section; the relaunch then takes resume-from-run-id and
  re-dispatches only the lanes with no completed checkpoint. One large verification fan-out was
  killed mid-run by a primary-model quota wall with roughly half its agents complete; because
  every finished agent's output was checkpointed under the run id, the relaunch resumed from that
  id and re-dispatched only the unfinished lanes — the completed half was never re-run or
  re-rolled. Fallback (principle 35) and resume defend different halves of the batch: fallback
  keeps agents alive *through* the wall, resume keeps finished work *through* the interruption.
  Re-running a completed agent pays twice for reviewed work — and re-rolls outputs a reviewer may
  already have read.
- **Deterministic work runs as scripts, not reasoning.** Running a script is cheaper, faster, and
  more reliable than having a model re-derive the same steps every iteration (loop guide); reserve
  inference for genuine judgment points. At each pipeline stage ask: is this
  routing/labeling/formatting decidable by rules? If yes, write the hundred-line script — one team
  routes its issue triage with a ~130-line rule script and zero LLM calls — and tripwire the LLM
  upgrade behind recorded evidence that the rules actually fail, which is precisely the
  pre-committed tripwire principle 30 records ("LLM triage only after three real misroutes").
- **A below-bar iteration is a defect in the system around the loop, not in the instance.** The
  quality of loop output is set by the skills, guards, preflights, and conventions the model works
  inside (loop guide). Encode each correction as a durable mechanism — a guard test, a drift
  preflight, a skill carrying the verification steps — so every future iteration inherits it; patch
  only the instance and the same failure recurs on schedule. This is principle 28's postmortem
  corollary applied *pre*-incident, inside the loop: one team turned a five-bug review round on a
  single feature into class-level guards (a write-boundary check, an idempotency test, a
  revisit-leg regression) plus a CI drift preflight, rather than five point fixes.
- **Every iteration's product lands in files, not conversation.** Output that exists only in
  ephemeral context cannot be traced, resumed, or audited after interruption (Weng). This is
  already the standing rule for dispatches — the handoff artifact
  (`07-multi-agent-parallel-work.md` § Handoff Artifact) and the append-only log
  (`14-async-multi-agent-collaboration.md`) — the loop-specific addition is process-manager
  discipline for whoever runs the loop: launch, inspect logs, cancel failed runs, merge results.

## Cost-Tiered Composition

Principle 35 fixes the **static** layer of model composition: a checked-in routing table, one lane
per task nature, every lane with a declared fallback. That table routes *between* tasks. The
composition patterns below route *within* one task — a dynamic layer the table does not express.
(Note the distinction from `07-multi-agent-parallel-work.md`'s lead pattern, which is *role*
asymmetry — lead versus worker; these patterns add *model* asymmetry on top of it.) The organizing
claim: **the top-tier model rarely needs to run the whole task — top-tier solo is the composition
that carries the burden of proof, not the default.** Solo stays the right call for named shapes —
a short, judgment-dense task where the planning *is* the task, or an accuracy-critical lane where
the last few points of quality are the product — and principle 35's table already routes whole
reasoning-dense lanes that way; record such a lane as *deliberate* in the routing table's
comments, never as an unexamined default.

| Pattern | Expensive model | Cheap model(s) | Vendor-reported (source) | Choose when |
| --- | --- | --- | --- | --- |
| **Advisor** | consulted only at decision junctures | executes the entire task, pausing to consult | ≈92% of the expensive model's solo SWE-bench Pro score at ≈63% of its cost — often a single consult per task (Anthropic advisor/orchestrator docs) | execution-heavy work with rare genuine forks |
| **Orchestrator** | plans, splits, synthesizes — touches few tokens | do all token-heavy reading/writing in parallel contexts | ≈96% of BrowseComp performance at ≈46% cost — $1.61 vs $4.00, 194 s vs 608 s, identical verification standards (`managed_agents/CMA_plan_big_execute_small.ipynb`) | planning/synthesis-heavy work with bulk I/O |

Both rows are **vendor-reported** — Anthropic measuring its own models, on its own benchmarks, in
its own harness; nothing here replicates them. Treat them exactly like the STOP claim in the next
section: externally attributed until your own control experiment (principle 16) makes them local
fact.

- **Choose by task shape; the routing table sets the lane default, the brief may override it.**
  Execution-heavy with occasional hard calls → advisor; planning- and synthesis-heavy over a wide
  reading surface → orchestrator. The routing table's per-lane composition is the lane default; the
  brief may override it per task; an override is recorded in the handoff. An unrecorded composition
  choice gets re-decided differently by every future dispatcher — the same failure principle 35
  names for routing decided in chat.
- **A static routing table is the coarse form of the orchestrator pattern — name the refinement you
  have not adopted.** One team's per-lane table (reasoning-dense lanes to the deepest reasoner,
  execution-dense lanes to the workhorse) is orchestration *between* tasks; within-task advisor
  switching — the cheap executor pausing mid-task to consult — was the dimension it had not
  adopted, and wrote down as such. An unadopted refinement named in the table's comments is a
  decision; unnamed, it is a blindspot.
- **A juncture is declared in the brief, and a consult is a logged event.** Three copyable juncture
  declarations: *consult before any change to a shared contract or schema*; *consult before any
  irreversible step — a migration, a deletion, an external side effect*; *consult when two or more
  designs pass the tests and the choice is judgment, not measurement*. Mechanism, one sentence per
  harness: with subagents, the executor invokes a subagent pinned to the advisor model and hands it
  the juncture question; without them, the executor halts at the declared juncture and a human
  relays the question to the expensive model and pastes the ruling back; on a bare API, a
  `consult(question, context)` wrapper bound to the advisor model is the only escalation path the
  executor's prompt licenses. Executable form: the handoff artifact
  (`07-multi-agent-parallel-work.md` § Handoff Artifact) gains a `consults:` field — one line per
  consult: juncture · question · ruling · cost — and review reconciles the count against the
  declared junctures: zero consults on a task whose brief declared junctures is a Deviations check
  (`15-finding-your-unknowns.md`); zero consults on a fork-free task is the advisor economics
  working.
- **A model tier is leased on two clocks, and principle 35 already owns one of them.** The quota
  clock — what a lane degrades to when the window empties, and how a fired fallback is annotated in
  the handoff for operators (principle 11) — is principle 35's territory, via the routing table's
  existing `on_quota_exhaustion`; do not restate it. The lease adds the **calendar** clock,
  principle 26's shape at the model boundary: a promotional, trial, or contract-bound tier has an
  expiry date, a renewal owner, and a pay-to-renew decision. Executable form:
  `templates/MODEL_ROUTING.template.yaml` gains a top-level `models:` section — one lease block per
  model, lanes reference models by name — with exactly three fields:

  ```yaml
  models:
    frontier-alpha:
      lease:
        expires: 2026-09-30            # date, or `none` for owned/self-hosted tiers
        renewal_owner: founder
        on_calendar_expiry: degrade-to workhorse-b   # or: renew / defer
    workhorse-b:
      lease:
        expires: none
        renewal_owner: n/a
        on_calendar_expiry: n/a
  ```

  The Dispatch Preflight (`07-multi-agent-parallel-work.md`) fails only on a missing lease block or
  a lane whose primary is past its declared `expires`; `expires: none` is legal and passes. Quota
  behavior stays where it already lives: the lane's `on_quota_exhaustion`.

## Harness Self-Improvement Boundaries

Weng's central move is to treat the harness — the loop code, the prompts, the tooling around the
model — as software the agent itself can improve. This playbook agrees; most of its own machinery
was built that way. The boundaries below are about what the improving loop must never reach, and
what evidence admits a mechanism change.

- **The evaluator, the permission layer, and the control-plane configuration live outside the loop
  they judge.** A self-improving loop optimizes whatever signal it is given — overfitting tests,
  gaming judge models, exploiting benchmark gaps (Weng's reward-hacking warning). Two distinct
  boundaries follow, and they are not the same rule: principle 31 forbids *editing* — the gate
  guards its own files, verdicts SHA-bound per `10-prompt-and-model-output-contracts.md` § Review
  Verdicts Are Model Outputs Too, reviewer family diversity per principle 14; this boundary forbids
  *fitting* — the loop must not optimize against the evaluator's observable signal. The fitting
  defenses are the new machinery here: held-out checks whose signal the loop never observes while
  iterating; a scoring rubric whose details are not disclosed to the loop being scored; and changes
  to the evaluator or its policy routed through the *highest* gate — the level no agent may approve
  on the operator's behalf, a human ruling — as one team's control policy states outright: editing
  the policy table is itself a top-level gated change.
- **Accept a mechanism change only on held-in AND held-out no-regression.** Weng's Self-Harness
  account accepts a harness modification only when a held-in check confirms the targeted weakness
  is actually fixed *and* a held-out check confirms nothing else broke — a double gate that blocks
  both placebo fixes and regressions smuggled in by the fix; rejected candidates are logged, not
  discarded. The DoD gate already has the shape: per-fix tests are the held-in leg, the scripted
  end-to-end smoke on hostile fakes (principle 27) is the held-out leg. The corollary is **guard
  continuity**: never remove or replace a system's only regression guard before the successor
  guard exists — one team's audit ruled exactly this, requiring the end-to-end guard's replacement
  to land before deleting the only artifact that exercised it. "The targeted test passes" is half
  the acceptance criterion, never all of it. Executable form: the review packet for any change to
  CI, gates, or harness machinery answers three questions — what is held-in, what is held-out,
  which guard covers the gap while this lands.
- **Record the causal mechanism of a failure, not its surface error.** Models are trained on
  success-skewed data and under-report failure, yet failed attempts are the cheapest way to prune a
  search space — so the harness must make saving them the path of least resistance, and the record
  must capture direct cause, causal state, and abstract mechanism: two runs with identical surface
  error logs can have entirely different root causes, and a symptom-level record misroutes the next
  fix (Weng). The playbook already lands two classes: adjudicated no's go to the residual ledger
  (principle 30), in-flight plan departures go to the handoff's Deviations
  (`15-finding-your-unknowns.md`). The class neither owns is **negative evidence** — experiments
  tried and abandoned, rejected mechanism candidates, dead-end prototypes. Give it a home and a row
  format: `templates/NEGATIVE_EVIDENCE.template.md`, instantiated next to the repo's residual
  ledger — one row per abandoned attempt: what was tried · against which model/version/date ·
  direct cause · causal state · abstract mechanism · why abandoned. Example row:
  `2026-06-17 · structured tool-output streaming on <model X, 2025-12 rev> · cause: JSON
  truncated near 4k tokens · state: provider output cap hit mid-object · mechanism: hard provider
  cap, not a schema fault · abandoned: cap not configurable; recheck on next model rev`. And "path
  of least resistance" is itself a mechanism, not a wish: the handoff artifact gains a required
  `negative-evidence:` field — the attempts abandoned during this dispatch, or the literal word
  `none`. Date-stamp capability negatives, because they expire — a negative result on last
  quarter's model is not a negative on this quarter's, the mirror image of the stale-seeding
  failure in which a research brief anchored an agent a model generation back. When a negative
  hardens into a ruling, promote it into the residual ledger as a `never` row with its tripwire
  (principle 30); until then it is evidence, and its whole job is to stop the next agent from
  re-running the experiment.
- **Defend the proposal population against diversity collapse.** A weak or fuzzy evaluator applied
  repeatedly converges its candidate population; Weng cites novelty rejection-sampling
  (ShinkaEvolve) as the population-level defense — reject non-novel candidates before spending
  evaluation on them. The playbook's incumbent defense at the decision level is principle 33's
  opposed charters and total-cost accountant; the loop-level addition: mechanism proposals diff
  against the never-do ledger (already required by `08-review-and-delivery-checklists.md`) *and*
  against the repo's `NEGATIVE_EVIDENCE.md`. A loop that re-proposes its own dead ends is the
  self-inflicted version of the new agent re-proposing a rejected architecture.
- **Recursive structure is not a substitute for base capability.** STOP (Zelikman et al., 2023,
  via Weng) found a recursive self-improver works on a strong base model and gets *worse* on weaker
  ones — the scaffold pays off only when the base is capable enough to improve the mechanism
  itself. Practically: route mechanism-design, judgment, and meta-level work to the deepest
  reasoner available — this is the external evidence behind the routing table's dated task-nature
  note, which principle 35 deliberately keeps as project policy rather than principle — and do not
  expect loop architecture to rescue a base that cannot verify its own steps. Stated honestly:
  this claim is externally attributed; run your own control experiment (principle 16) before
  treating the strong form as local fact.

## The Agent's Own Failure Modes

Trehan & Chopra (2026, via Weng) catalog six recurring failure modes of autonomous
research/engineering agents. They are the **cognitive** complement of the dispatch-mechanics list
in `07-multi-agent-parallel-work.md` § Agent Failure Modes To Plan For — a different axis, with one
named abutment: mode 1 abuts 07's understand-maps bullet, where 07 owns the pre-edit mapping
discipline and this table owns the training-prior bias that survives it; neither list replaces the
other. Do not stand up a third list — and do not let this one fork either: **the canonical
enumeration of the six is the Blindspots prompt list in `templates/AGENT_TASK_BRIEF.template.md`**,
landed by this change with the prompts quoted below; this table is commentary — the defense
mapping — and where the two diverge, the template wins. Any instance observed in the field lands as
a row in `13-operator-decisions-and-evidence-integrity.md` § Pitfall Log, the repo's one home for
realized pitfalls.

| # | Failure mode | Looks like | Brief-level defense (each with a pasteable line) |
| --- | --- | --- | --- |
| 1 | **Training-data default bias** | stale library/model versions; assumptions grounded in the training set, not this repo | Blindspots "this repo's conventions" + the freshness rule: every external version or capability claim is queried live and dated — one team's research agent, seeded with an old version list, anchored on it and missed two newer releases; reference implementations ride in Context. Pasteable: "Every version/capability claim in this brief was checked live on <date>; nothing is seeded from prior notes." |
| 2 | **Implementation drift under pressure** | quietly switching to a simpler, more common approach mid-task | the Deviations discipline (`15-finding-your-unknowns.md`): departures recorded with pinning tests; a contract-direction change is a Stop Condition, not a deviation. Pasteable: "Constraint: use <approach X>; switching to <the common simpler approach Y> is a Stop Condition, not a deviation." |
| 3 | **Memory/context decay** | long-run knowledge evaporates because logs were never persisted | implementation notes per dispatch; handoffs written to the append-only log (`14-async-multi-agent-collaboration.md`); the in-flight recording protocol (WIP commits, resume card) is `21-interruption-safe-handoff.md`. Pasteable: "Write findings to implementation-notes.md as you go; nothing may exist only in this conversation." |
| 4 | **Overclaiming on noisy or failed results** | "p-hacking eureka" (Bubeck, 2025): success declared on evidence that does not reproduce | DoD is evidence, not compilation (`13-operator-decisions-and-evidence-integrity.md` — unreproducible-claims row); attribute a failure before owning it (principle 16). Pasteable: "Success = <exact command> printing <literal expected output>; paste the actual output, not a paraphrase, into the handoff." |
| 5 | **Missing domain tacit knowledge** | competent-looking work that violates the field's unwritten rules | Blindspots "prior art" + the interview-me elicitation (`15-finding-your-unknowns.md`); a reference implementation as the spec prose cannot write. Pasteable: "Before writing code, list three unwritten rules of <domain> this change could violate, and check each against the reference implementation in Context." |
| 6 | **Missing taste** | effort flows to the wrong question; the important call is made casually | plans open with change-prone decisions (`15-finding-your-unknowns.md`); Non-Goals fence the rest. Pasteable: "The one call here that must not be made casually is <X>; it routes to the decision queue as a card (principle 34), not into the diff." |

The six prompts, verbatim — copy them unedited into the template's Blindspots list; the dispatcher
answers each per task, or writes why it does not apply:

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

The executable form of this section is the template edit above — the six prompts, copied verbatim.
A brief that cannot say which of the six applies to *this* dispatch has not been thought through —
the cure for an unknown known is a form with a blank that will not stay blank.

## Checklist

- [ ] Every delegated loop can name its rung; new loops started at rung 1–2; every climb was
      unlocked by the pre-declared metric (default: three consecutive runs, zero human corrections,
      stop condition self-fired — not the cap, not the human).
- [ ] Every climbed rung has a dated grant row in the ledger (date · rung N→N+1 · metric observed ·
      evidence link), and each rung's grant row predates the one above it — the auditable form of
      "verification before stop, stop before trigger, trigger before prompt".
- [ ] Routine intervals match the watched object's real change rate and each routine carries a
      `revisit_when` date; anything with a platform event uses the event, not a poll; proactive
      loops are silent when empty.
- [ ] Every non-review loop's brief carries the three Stop Conditions lines — deterministic stop
      criterion where one exists, attempt/budget cap, trigger with justification — before launch
      (review rounds terminate per principle 29); its board row carries an `expected-done`.
- [ ] Fan-outs above the preflight threshold (more than 5 agents or over $50 projected,
      repo-configurable) ran a pilot slice first; the dispatch log's required pilot-findings field
      says what the full run's configuration changed.
- [ ] Every fan-out carries a run id and lands each completed agent's output in files keyed by
      it; a relaunch after interruption resumes from the run id and re-dispatches only lanes with
      no completed checkpoint — survivors are never re-run or re-rolled.
- [ ] Rule-decidable pipeline stages are scripts; the LLM upgrade for each is tripwired behind
      recorded evidence that the rules fail.
- [ ] A below-bar iteration produced a system fix (guard, preflight, skill) inherited by all future
      iterations — not only an instance fix.
- [ ] Within-task composition follows the routing table's lane default unless the brief overrides
      it, and the override is in the handoff; unadopted refinements and deliberate top-tier-solo
      lanes are named in the table's comments; the handoff's `consults:` lines reconcile against
      the brief's declared junctures at review.
- [ ] Vendor-reported composition numbers are treated as externally attributed until a local
      control experiment (principle 16); top-tier solo carries the burden of proof, not the
      default slot.
- [ ] Every model in `templates/MODEL_ROUTING.template.yaml`'s `models:` section declares
      `expires` / `renewal_owner` / `on_calendar_expiry` (`expires: none` legal for owned tiers);
      the dispatch preflight fails a lane whose primary's lease block is missing or past its
      `expires`; quota behavior stays in the lane's `on_quota_exhaustion`.
- [ ] The evaluator, permission layer, and control-plane config are unreachable from inside any
      self-improving loop — not editable (principle 31) and not fittable (held-out signals
      unobserved in-loop, undisclosed rubric, version-bound verdicts); evaluator changes go through
      the highest gate — the level only a human ruling can pass.
- [ ] Mechanism changes are accepted only on held-in + held-out no-regression; no only-guard is
      deleted before its successor exists; rejected candidates are logged.
- [ ] Failure records capture all three depths — direct cause, causal state, abstract mechanism — not
      the surface symptom alone; negative
      evidence lands as dated rows in the repo's `NEGATIVE_EVIDENCE.md` (or the literal `none` in
      the handoff's `negative-evidence:` field); capability negatives expire; hardened negatives
      promote to the residual ledger as `never` rows.
- [ ] Every brief's Blindspots section is answered against the template's canonical six prompts
      (this doc's table is commentary — the template wins on divergence); observed instances land
      in `13-operator-decisions-and-evidence-integrity.md` § Pitfall Log, never in a new list.