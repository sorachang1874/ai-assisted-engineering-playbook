# Contract: <Name>

## Purpose

Define what this contract governs.

## Owners

| Area | Owner | Notes |
| --- | --- | --- |
| Write model |  |  |
| Read model |  |  |
| API |  |  |
| UI |  |  |
| Tests |  |  |

## Source of Truth

Describe the canonical source of truth. State explicitly what is not a source of truth.

## Field Matrix

| Field | Owner | Source | Allowed Values | Derivation | Lifetime | Consumers | Fallback | Migration | Deletion Condition | Preflight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |

Lifetime (required for reference-typed fields — URL/token/session/handle):
`durable | request-scoped | leased(ttl, expiry-strategy = materialize | re-mint | refresh)`.
A leased reference is never persisted un-converted; enforcement is a constructed write-boundary
guard, not this row (principles 26/28).

## Actions (Verbs)

For every user-facing action this contract governs (principle 25). Each clause must reduce to an
executable form — a failing test, a rejected write, a lint — or it is not implemented.

| Action | On repeat (idempotency + where enforced) | Ack surface | User failure render | Operator failure signal |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

Actor model assumed: the trigger repeats (incl. network retry), the feedback is missed, every
produced artifact is revisited after arbitrary delay, the flow can die mid-action.

## State Transitions

| From | Event/Command | To | Owner | Idempotency Key |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Failure Behavior

- Retry policy:
- Timeout:
- Cancellation:
- Late result:
- Partial result:
- Quarantine:

## Public API Behavior

- Ready behavior:
- Not-ready behavior:
- Permission behavior:
- Fail-closed behavior:

## Preflight

Command:

```sh
make test-contract
```

Checks:

- 

## Migration and Deletion Plan

| Bridge | Visibility | Normal-path allowed? | Deletion condition |
| --- | --- | --- | --- |
|  |  |  |  |

