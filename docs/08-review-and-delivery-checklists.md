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
