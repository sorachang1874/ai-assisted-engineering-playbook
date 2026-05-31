# Review and Delivery Checklists

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

## Implementation Review

Before merging:

- Search all usages of changed symbols.
- Update all producers and consumers.
- Add regression tests for previous failure mode.
- Add or update fast preflight.
- Update docs and TODO status.
- Verify no hidden fallback was introduced.
- Verify realistic payloads when mocks are insufficient.

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

