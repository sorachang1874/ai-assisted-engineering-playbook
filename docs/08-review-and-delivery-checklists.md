# Review and Delivery Checklists

## Gate Types

Use different gates for different kinds of approval:

| Gate | Timing | What It Approves | What It Does Not Approve |
| --- | --- | --- | --- |
| Design Gate | before implementation | problem framing, contracts, artifact chain, boundaries, validation plan | code is correct, runtime execution, adoption |
| Implementation Gate | after code, tests, and sample artifacts | implementation matches accepted contract | publication, scheduling, defaults, production claims |
| Adoption Gate | before changing defaults or exposing outputs | current/default/public/scheduled behavior is safe | unrelated future work |

A `GO` is scoped to the named gate only. It should not be reinterpreted as
approval for later gates.

## Required Review Packet

For any non-trivial gate, include a review packet with:

- objective, non-goals, enabled decisions, and still-blocked decisions;
- contract or schema changes;
- artifact chain and downstream consumers;
- evidence classification;
- boundary flags;
- validation commands and exact results;
- generated artifacts and reports;
- claims to verify.

If the packet is missing for a milestone, contract change, output-chain change,
external execution, secret handling, adoption, or effectiveness claim, the
review package is incomplete.

For HOW to run the reviewer (cross-model configuration, one-shot invocation,
stdin/pipe pitfalls), see the Cross-Model Review Runbook in
`07-multi-agent-parallel-work.md` § Independent Review Gate.

## Gate Trigger Matrix

Use an independent review gate when a change affects any of these surfaces:

| Trigger | Minimum Gate | Why |
| --- | --- | --- |
| Contract or schema change | Design Gate before implementation; Implementation Gate after code | Prevents producers and consumers from diverging. |
| New artifact chain, cache, report, queue, handoff, or manifest | Design Gate | Ensures outputs can be consumed, reviewed, redacted, and retired. |
| Milestone implementation or completion | Implementation Gate | Verifies the completed slice supports the intended decision. |
| External calls, live providers, remote execution, or scheduling | Design Gate plus Implementation Gate | Controls cost, rate limits, secrets, environment, and auditability. |
| Secret or private-resource handling | Design Gate plus Implementation Gate | Prevents secret reads, secret emission, or private data leakage. |
| Generated output that could be published or used by users | Implementation Gate and Adoption Gate | Separates internal evidence from public or user-facing claims. |
| Defaults, runtime modes, feature flags, or profile/config mutation | Adoption Gate | Confirms the current artifact is safe to become normal behavior. |
| Effectiveness, quality, production-readiness, or account-risk claims | Adoption Gate or evidence-specific review | Prevents diagnostic or partial evidence from becoming a broad claim. |
| Toolchain or workspace dependency change affecting evidence | Design or Implementation Gate | Keeps environment drift from invalidating later runs. |
| Operator override, exception, or manual decision application | Per-batch independent review of the exact decision file, recorded and machine-verified | Prevents unreviewed human decisions from flipping derived state; see `13-operator-decisions-and-evidence-integrity.md`. |

A gate is not needed for every typo, comment, or isolated test fixture. It is
needed when future agents, operators, users, or automation may interpret the
change as stronger evidence or permission.

## Cross-Model Gate Review

An independent gate is only independent if the reviewer is a **different model
family** than the one that authored and self-critiqued the artifact (principle
14). Operate gates this way:

- The author model runs a multi-lens **adversarial self-critique** first (cheap;
  removes the obvious issues), then the artifact goes to a **cross-model gate**
  for the binding verdict. Same-family agreement is weaker evidence than one
  cross-family verdict.
- Give the cross-model reviewer the same review packet plus the ability to
  independently re-derive and *run* the checks (read the code, run the tests,
  grep the artifacts) rather than trusting the packet's prose.
- The verdict vocabulary is the same `NO-GO` / `GO WITH FIXES` / `GO`. A
  `GO WITH FIXES` that verifies the substantive properties is the real signal;
  apply the fixes and record it, as with any gate.
- **For a fail-closed validator specifically** (principle 15): build it as a
  canonical-shape **allowlist**, keep the canonical shape as a single source of
  truth the generator emits and the checker deep-equals, and add a cross-language
  **parity** check. Expect an adversarial cross-model reviewer to keep finding
  ever-rarer structural edge cases (duplicate/shadowed names, unresolved graph
  references); fix the real ones, but decide the practical stopping bar rather
  than chasing an asymptote of inputs the generator never produces.
- **Run a source-of-truth audit before the gate, not extra self-critique rounds**
  (principle 18). The cross-model gate's distinctive findings are *doc-grounded* —
  a misused config semantic, an unhandled default, a `!=`/wildcard/set spelling, a
  last-assignment reset, or a value the upstream tool *requires* that the validator
  wrongly rejects. Same-family adversarial rounds converge on same-family blind
  spots and cannot surface these — they share the author's mental model and may even
  *confirm* a wrong guard. So cap the self-critique at one or two multi-lens rounds,
  then — before opening the gate — open the upstream reference doc for every external
  surface the artifact inspects or emits and verify each against it. This collapses a
  string of gate round-trips, each surfacing one doc-grounded class, into one
  self-audit pass plus a confirming gate. When the validator is a canonical-shape
  allowlist, the audit reduces to one question — "does the canonical shape match the
  upstream schema?" — instead of enumerating every unsafe deviation.
- **Spend round-trips on classes, not lines** (principle 19). A gate round-trip is
  serial and high-latency, so minimize the *count* of rounds, not the findings per round.
  Make the pre-gate self-critique cover *every* surface the gate audits — not only the
  mechanical validator but the runbook's sequencing, the renderer/generator's
  side-effects, and the docs' inventories/counts/cross-references — run as parallel lenses
  (principle 7) so discovery is cheap and local. Then respond to each finding by fixing
  its whole *class* (every sibling path with the same property) and the *ripple* of any
  canonical/emitted-shape change (stale-artifact cleanup, perms, doc inventories,
  validation coverage, cross-refs) in the *same* round, plus the adjacent class the gate
  hasn't asked about yet. Batch the long tail: at "no blockers, a few minor findings," do
  one consolidated fix pass and a single confirming gate rather than a round-trip per
  cosmetic fix. The reviewer should be *confirming* a class is closed, not enumerating its
  members for you one round at a time.
- **Terminate the gate — classify each round's findings into three bins (principle 29).**
  (a) A *new fixable class* → fix it with its siblings and ripple in one round (principle 19);
  (b) an *already-fixed class re-cited* → the finding must point to the specific commit or gate
  round that fixed the class; (c) a *residual unfixable under the current trust or architecture
  model* → the finding must cite a `templates/RESIDUAL_LEDGER.template.md` entry id (principle 30).
  A finding that can point to neither defaults to (a) and blocks; the classification is confirmed
  by the lead or a human, never declared unilaterally by the author's agent. **Stop rule:** feed
  the full residual ledger to each round; when a round produces only (b) and (c), stop — an
  all-cited round resolves as "no new information — pass with recorded residuals," while any
  finding that cites no ledger entry still blocks. An unterminated gate blocks forever or trains
  the team to skim it.
- **Retro-validate a new gate before it blocks (principle 32).** Pre-declare the decision rule
  in copyable form: retro-run the gate against the two or more most recent merged, human-reviewed
  changes; **≥ one finding the author confirms would have required a code change ⇒ the gate earns
  its blocking posture; zero such findings ⇒ it ships advisory-only** with a re-evaluation
  scheduled (90 days or a fixed run count). Attach the retro-run transcript to the installation
  change and carry a retro-validation evidence reference in the review packet's gate section
  (`templates/REVIEW_PACKET.template.md`). Retro-validation decides when a gate *starts* blocking;
  the termination rule above decides when a given review *stops*.
- **Diff every new-mechanism proposal against the never-do ledger first (principle 30).** Before
  a proposed gate, automation, or architecture is argued on the merits, check it against the
  `status: never` rows of `templates/RESIDUAL_LEDGER.template.md`; a proposal that re-raises a
  ratified never-do is closed by the ledger entry unless it presents the reopen-evidence that
  entry names.
- **A harness/mechanism change passes a double evidence gate — held-in AND held-out (principle 38;
  `16-loops-and-model-composition.md`).** First ask: *does this change touch a signal some loop
  optimizes against? — then that loop's own outputs are inadmissible as the change's evidence.* A PR
  that edits CI, a gate, a rubric, a judge model, or any harness machinery carries two evidence
  fields — **held-in** (the targeted weakness is actually fixed) and **held-out** (a signal the loop
  never observed while iterating confirms nothing else broke); "the targeted test now passes" is
  half an acceptance criterion, never all of it. A deletion or replacement of a system's *only*
  regression guard with no named successor guard fails review — the successor guard lands first. And
  before the change spends a run, its proposal is diffed against `templates/NEGATIVE_EVIDENCE.template.md`
  (principle 39) as well as the never-do ledger above: a loop that re-proposes its own dead ends is
  stopped exactly as a new agent re-proposing a rejected architecture is.
- For the operational how-to — the reviewer model/reasoning/service-tier
  configuration, the canonical one-shot invocation, the `< /dev/null` stdin rule,
  the never-pipe-codex-through-`tail` rule, the hard timeout and read-only sandbox
  — see the **Cross-Model Review Runbook** in `07-multi-agent-parallel-work.md`.
  Friction to expect: the agent's own sandbox may lack a network path to the
  external reviewer; run the gate from the human's host shell or a clean egress
  path.
- **Async (non-blocking) reference lane.** For a change *already* covered by
  independent adversarial sub-agent verification, the cross-model gate can run as a
  non-blocking reference channel rather than a blocking gate: fire it in the
  background (read-only, `--base` pinned to a commit) while the primary
  verification runs; proceed on the primary verdict; triage the cross-model result
  when it lands — real findings fixed forward, false positives recorded. Never roll
  back landed work solely because the reference review is still pending. Destructive
  or non-rebuildable-asset operations keep the blocking gate; the async lane never
  applies to them (principle 14).

## Review Packet Quality Bar

The packet should make review possible without chat history. It should include:

- the exact decision this gate must make;
- the decisions that remain blocked;
- changed files and generated artifacts;
- schema versions and required fields;
- producer, consumer, retention, and overwrite policy;
- evidence class and promotion boundaries;
- boundary flags for external calls, DNS/network discovery, secret reads,
  cache writes, reviewed facts, publication, scheduling, and user-facing output;
- validation commands with exact pass/fail results;
- sensitive-output scan scope and result;
- known missing context, missing tools, or unverified inputs.

If the packet omits known missing context, reviewers should return `GO WITH
FIXES` or `NO-GO` depending on whether the missing context can change the
decision.

**Pair the packet with an explicit output contract — demand an exhaustive,
severity-ranked findings list, not a verdict with two or three points.** Round count
is dominated by reviewers that *stop enumerating once the verdict is decided*: the
first blocking finding settles a `NO-GO`, so the review returns a handful of issues,
you fix them, and the next pass surfaces the next handful — N rounds for what could
have been one. Counter it in the review request:

- **Exhaustiveness over verdict.** State plainly: "do not stop at the first blocking
  issue; enumerate *every* issue you can find in this pass — the complete ranked list
  matters more than the verdict."
- **Severity + confidence per finding.** Require each finding tagged P0 (a real
  leak/violation passes) / P1 (weakens a guarantee) / P2 (correctness/nit), and
  *ran-and-confirmed* vs *doc-reasoned*, with the exact repro (mutation + command +
  output) and the doc citation. This lets you batch-fix everything at once and weight
  by confidence instead of round-tripping per finding.
- **Front-load the context that prevents wrong diagnoses and re-treading.** Give the
  reviewer the already-closed-issue list with citations (so its budget goes to novel
  classes), the threat model / invariants, the *reviewer environment's* limits (e.g.
  the target binaries are not installed, so behaviour is doc-grounded — say so rather
  than letting it discover this), and which surfaces you have already audited against
  which docs (principle 18). A coverage checklist of surfaces to sweep makes breadth
  explicit rather than discretionary.

## Design Review

Before accepting a design, check:

- Does it reduce or add sources of truth?
- Is the owner/source-of-truth matrix complete?
- Are partial states explicit?
- Are retries and cancellation defined?
- Are provider costs and rate limits controlled?
- Is user-visible wording coherent during in-flight states?
- Is there a deletion plan for old paths?
- Can an agent operate it through stable APIs?
- Are plan-only artifacts separated from execution artifacts?
- Are evidence classes and promotion boundaries explicit?
- Is every status enum value reachable by some input and handled by some
  consumer branch, with the consumer's apply logic total over its input
  combinations?
- Do new consumers of evidence only degrade or maintain existing
  interpretations, with any new score cap cross-checked against every cap
  that already binds in the same state?
- Does the design name every existing function it modifies, not only the new
  code it adds?

## Implementation Review

Before merging:

- Search all usages of changed symbols.
- Update all producers and consumers.
- Add regression tests for previous failure mode.
- Add or update fast preflight.
- Update docs and TODO status.
- Verify no hidden fallback was introduced.
- Verify realistic payloads when mocks are insufficient.
- Verify malformed input produces fail-closed artifacts or issue counts where
  appropriate.
- Verify generated JSON, reports, queues, handoffs, and manifests are scanned
  for sensitive output.
- Verify reviewed snapshots or digests prevent drift between review and
  execution, and that consumers verify every recorded input digest, not a
  subset.
- Verify dry-run and sample artifacts cannot be interpreted as stronger
  evidence than their boundary flags allow.
- Verify tools or dependencies discovered missing during implementation are
  tracked as follow-up work, not left only in chat history.
- Before attributing any post-change test failure to the change, run the control
  experiment: re-run the failing test on the pinned pre-change baseline (in a
  parallel worktree, not by flipping the shared working tree). Identical failure
  means pre-existing — record it in the known-failure budget and do not "fix" it
  under this change (principle 16).
- Verify the change imports and runs from a clean checkout, not only from the
  working tree: tracked code must not import an untracked local module, and any
  oracle or test must route to where the code actually runs (principle 14).

## Adoption Review

Before replacing defaults, enabling schedules, publishing artifacts, or making
user-facing claims:

- Confirm Design and Implementation Gates passed for the same scope.
- Inspect generated current artifacts, manifests, reports, and status views.
- Confirm boundary flags explicitly allow the adoption action.
- Confirm residual blocked items remain visible.
- Confirm ready handoffs are not being counted as completed execution.
- Confirm publication/redaction checks cover generated outputs, not only source
  code.

## Runtime Review

For long-running workflows:

- Events are append-only.
- Commands are typed and owner-mapped.
- Activities are bounded and idempotent.
- Worker leases recover from crashes.
- Retries are item-level where possible.
- Late provider results are quarantined or causally attached.
- Read models are materialized and fail closed.

## Signoff Review

Before declaring a phase complete:

- Targeted tests pass.
- Contract preflight passes.
- Integration or smoke path passes.
- Migration bridge usage is zero or explicitly tolerated.
- Metrics reflect typed causality, not heuristic timestamp pairing.
- Residual risks are documented.
- Any remaining test failures are accounted for by the known-failure budget, each
  entry control-attributed to a pre-existing cause (principle 16), not silently
  tolerated.
- Skip counts in gating lanes are zero or REQUIRE-gated: environment-dependent
  fixtures ran fail-closed, with a zero-skip or pinned collected-count assertion —
  a lane that can mass-skip its subject is not evidence (principle 40).
