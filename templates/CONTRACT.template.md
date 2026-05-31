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

| Field | Owner | Source | Allowed Values | Derivation | Consumers | Fallback | Migration | Deletion Condition | Preflight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |

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

