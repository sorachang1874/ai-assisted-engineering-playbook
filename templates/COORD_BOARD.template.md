# Coordination Board

Lead-owned live projection. Checked-in delivery graphs are authoritative.

## Run

| Field | Value |
| --- | --- |
| Product objective |  |
| Run id |  |
| Repository |  |
| Delivery graph |  |
| Graph commit |  |
| Integration owner |  |
| Last sweep |  |
| Next event/sweep |  |
| Distill due/trigger |  |

## Active and Ready Lanes

| Lane id | Owner | Graph/live status | Repo + branch/worktree | Declared writes | Exact verify | Expected done | Handoff/review | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |

Live status values: `unclaimed`, `claimed`, `active`, `waiting_external`,
`handoff_ready`, `integration_check`, `done`, `blocked`.

## Shared Hotspots

| Hotspot id | Current writer | Ordered next writer | Release evidence | Conflict |
| --- | --- | --- | --- | --- |
|  |  |  |  | none |

## Related-Repository Integration

No dirty-tree path or mutable runtime artifact belongs here. Each candidate is
pinned before the neutral integration batch starts.

| Product lane | Repository | Candidate commit | Capability envelope | Request/result/evidence versions | Local review | Integration status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Decision Queue

Only questions blocking a graph edge belong here. Durable rulings move to the
owning contract/decision artifact.

| Question id | Blocking lanes | Owner | Recommendation | Deadline/default | Log entry | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Sweep Result

- Newly ready lanes:
- Overdue/stalled lanes:
- Write-set drift or conflicts:
- Completed handoffs to verify:
- Review results to triage:
- Fixed-forward lanes to add:
- Cross-repository envelope/candidate drift:
- Distill trigger fired:
- Durable graph/status update needed:
