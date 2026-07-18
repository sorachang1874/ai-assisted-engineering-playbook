# Distill Candidate: TITLE

## Capture Metadata

| Field | Value |
| --- | --- |
| Candidate id |  |
| Captured by |  |
| Evidence window | commit/session/time range |
| Affected lanes |  |
| Measured cost | wall time, review rounds, conflicts, reruns, or manual steps |
| Recurrence | first / second / repeated |
| Synthesis trigger | milestone / weekly / recurrence / >30m rework / pre-scale |

## Observation

Describe the failure or inefficient behavior without proposing a solution yet.

## Evidence

- Exact artifact, commit range, command output, or coordination log:
- Counterexample or successful comparison, if available:

## Causal Mechanism

State why the behavior occurred. Prefer a reusable mechanism such as an
unmodelled dependency, shared write hotspot, hand-transcribed inventory,
global review lock, missing route, duplicated validation, non-restartable bulk
operation, or implicit cross-project dependency.

## Generalization Boundary

- Applies when:
- Does not apply when:
- Evidence still missing:

## Candidate Durable Change

- Project-local enforcement, playbook generalization, or no durable change:
- Construction/checker/template/manual gate:
- Owner and adoption path:
- Maintenance cost:
- Revisit or deletion condition:

## Synthesis Decision

- Status: captured / adopted / deferred / discarded
- Decision artifact or commit:
- Reason:
- Tripwire if deferred:
