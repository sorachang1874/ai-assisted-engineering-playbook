# Review Packet: <Phase Or Change>

Use this packet for design, implementation, and adoption reviews. The packet is
the reviewer's source of truth. Do not rely on chat history for required
evidence, scope, or safety boundaries.

## Gate

- Phase id:
- Gate type: Design Gate / Implementation Gate / Adoption Gate
- Requested verdict: `NO-GO` / `GO WITH FIXES` / `GO`
- Lifecycle step being reviewed:
- Previous gate evidence ref:
- This gate must decide:

## Objective And Non-Goals

- Objective:
- Non-goals:
- Decisions enabled if this gate passes:
- Decisions still blocked if this gate passes:

## Contract Changes

| Contract Or Schema | Change Type | Owner | Producer | Consumer | Compatibility | Deletion Or Migration Plan |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Artifact Chain

| Stage | Artifact | Schema | Visibility | Producer | Consumer | Redaction | Overwrite Policy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Raw/source |  |  |  |  |  |  |  |
| Intermediate |  |  |  |  |  |  |  |
| Report/status |  |  |  |  |  |  |  |
| Queue/handoff |  |  |  |  |  |  |  |

## Evidence Classification

- Plan-only evidence:
- Local diagnostic evidence:
- Clean runtime evidence:
- Remote-runner evidence:
- Private/paid redacted evidence:
- Public-source static evidence:
- External-provider evidence:
- Service-request evidence:
- Publication evidence:

## Boundary Flags

All flags must be explicit.

- External requests allowed:
- Provider calls allowed:
- DNS or network discovery allowed:
- Secret values may be read:
- Secret values may be emitted:
- Cache writes allowed:
- Reviewed facts may be created:
- User-facing output allowed:
- Publication allowed:
- Profile/config mutation allowed:
- Scheduled or remote execution allowed:

## Validation Package

- Fast preflight:
- Unit tests:
- Contract tests:
- Integration or dry-run tests:
- Generated JSON/JSONL/YAML artifacts:
- Generated Markdown or human reports:
- Sensitive-output scan:
- Manifest/public-safe check:
- Commands and exact results:

## Claims To Verify

1. 
2. 
3. 

## Known Risks

- 

## Reviewer Instructions

Inspect the complete packet plus the files listed here. Return `NO-GO`,
`GO WITH FIXES`, or `GO` for the named gate only.

- Files:
- Generated artifacts:
- Reports:
- Tests:

Do not approve downstream adoption, publication, scheduling, profile mutation,
live provider calls, or user-facing claims unless this packet explicitly lists
that scope and the required boundary flags are true.
