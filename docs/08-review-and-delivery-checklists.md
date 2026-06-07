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

A gate is not needed for every typo, comment, or isolated test fixture. It is
needed when future agents, operators, users, or automation may interpret the
change as stronger evidence or permission.

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
  execution.
- Verify dry-run and sample artifacts cannot be interpreted as stronger
  evidence than their boundary flags allow.
- Verify tools or dependencies discovered missing during implementation are
  tracked as follow-up work, not left only in chat history.

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
