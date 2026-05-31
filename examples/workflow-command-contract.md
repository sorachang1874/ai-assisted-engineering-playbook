# Example: Workflow Command Contract

## Command Type

`provider.search.submit`

## Owner

`provider_search_owner`

## Purpose

Submit a bounded provider search request for one logical item. A batch may contain multiple commands, but each command has a stable item ID.

## Envelope

| Field | Required | Purpose |
| --- | --- | --- |
| `command_id` | yes | Unique command row |
| `workflow_run_id` | yes | Execution scope |
| `operation_id` | optional | User/agent intent scope |
| `owner` | yes | Command owner |
| `command_type` | yes | Typed action |
| `causal_group_id` | yes | Links related activity/events |
| `source_event_id` | yes | Event that caused command |
| `parent_command_id` | optional | Upstream command |
| `idempotency_key` | yes | Deduplication |
| `not_before_at` | optional | Timer/retry scheduling |
| `attempt` | yes | Current attempt count |
| `max_attempts` | yes | Retry limit |
| `payload_json` | yes | Typed payload |

## Activity Mapping

| Activity | Trigger | Terminal Events |
| --- | --- | --- |
| `provider.submit` | claim command | submitted/failed |
| `provider.poll` | remote ref exists | complete/timeout/ignored |
| `provider.fetch` | dataset ready | fetched/failed |

## Retry Rule

Retry failed items, not the entire batch, unless the provider contract explicitly requires batch-level retry.

## Late Result Rule

If local polling was cancelled and the remote result arrives later, record it as quarantined evidence unless a command owner explicitly reattaches it.

