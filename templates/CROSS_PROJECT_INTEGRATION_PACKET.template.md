# Cross-Project Integration Packet: CAPABILITY

This packet owns convergence between independently developed products. It does
not authorize either product's agent to edit, import from, or call the other's
unfinished working tree.

## Integration Metadata

| Field | Value |
| --- | --- |
| Product objective |  |
| Integration owner |  |
| Integration repository/path |  |
| Delivery graph + commit |  |
| Review gate |  |
| Promotion target |  |

## Pinned Product Candidates

Dirty worktrees, moving branches, untracked modules, and mutable runtime output
are invalid candidates.

| Product lane | Repository | Exact candidate commit/build | Local tests | Local review | Runtime/mode owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Versioned Envelopes

### Capability envelope

- Capability id and version:
- Owner:
- Supported modes, targets, and lifecycle:
- Request/result schema references:
- Evidence class and promotion boundary:
- Unsupported behavior:

### Request envelope

- Schema id and version:
- Stable intent and scope:
- Requester/tenant ownership:
- Idempotency and causality fields:
- Policy/config pins:
- Unknown-field behavior:

### Result envelope

- Schema id and version:
- Success/partial/failure statuses:
- Artifact references and retention:
- Producer identity:
- Retry/replay semantics:
- Unknown-field behavior:

### Evidence envelope

- Schema id and version:
- Producer commit/build and runtime mode:
- Input/output/config digests:
- Validation and independent-review references:
- Evidence limitations:
- Consumer verification command:

## Independent Adapter Evidence

Each project proves its adapter against the frozen envelope fixtures without
calling the other project's unfinished runtime.

| Project | Adapter path | Fixture/version | Exact command and result | Candidate commit |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Integration Batch

- Exact candidate pair/set:
- Composition order and conflict policy:
- Cross-project identity/deduplication owner:
- Failure isolation and partial-result behavior:
- Consumer-visible comparison:
- Realistic integration command and expected denominator:
- Rollback/replay behavior:
- Outputs and digests:

## Boundary Preflight

- [ ] No shared dirty tree or untracked import.
- [ ] No implicit relative path into another product repository.
- [ ] No call to an unfinished or mutable peer runtime.
- [ ] Every candidate is pinned to an exact commit/build.
- [ ] Capability, request, result, and evidence envelope versions are exact.
- [ ] Both adapters pass independently against the same fixtures.
- [ ] Integration evidence names both producer candidates and all input digests.
- [ ] Integration has a separate owner, batch, validation, and review artifact.
- [ ] Local product review is not represented as integration review or vice versa.

## Review and Promotion

- Review packet/artifact:
- Findings/fixed-forward lanes:
- Residuals and tripwires:
- Decisions enabled:
- Decisions still blocked:
- Promotion record:
