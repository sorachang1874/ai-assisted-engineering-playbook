# Module: NAME

This file routes module questions to canonical artifacts. It should stay short
and contain links, ownership, boundaries, and validation entrypoints rather
than duplicated contract detail.

## Module Metadata

| Field | Value |
| --- | --- |
| Status | proposed / active / migrating / superseded / archived |
| Owner |  |
| Code boundary |  |
| Public surfaces |  |
| Last verified | YYYY-MM-DD |
| Next route audit | YYYY-MM-DD |

## Responsibility

Owns:

- Replace with an owned responsibility.

Does not own:

- Replace with an explicit non-responsibility and route it to its owner.

## Entry Points

| Surface | Path or symbol | Read when |
| --- | --- | --- |
| API/command |  |  |
| Worker/runtime |  |  |
| UI/CLI |  |  |
| Storage |  |  |

## Canonical Artifacts

| Artifact class | Canonical path | Owner | Status | Review trigger |
| --- | --- | --- | --- | --- |
| Contract | `docs/modules/<module>/contracts/<name>.md` |  | active |  |
| Product/prototype | `docs/modules/<module>/product/<name>.md` |  | active |  |
| Architecture | `docs/modules/<module>/architecture/<name>.md` |  | active |  |
| Testing | `docs/modules/<module>/testing/<name>.md` |  | active |  |
| Operations | `docs/modules/<module>/operations/<name>.md` |  | active |  |
| Migration | `docs/modules/<module>/migrations/<name>.md` |  | migrating |  |
| Decision | `docs/modules/<module>/decisions/<name>.md` |  | active |  |

Remove unused placeholder rows. Use real relative Markdown links after the
destination exists so link validation covers the route.

## Dependencies

| Direction | Module | Shared contract | Failure or change propagated |
| --- | --- | --- | --- |
| Upstream |  |  |  |
| Downstream |  |  |  |

## Validation

| Change class | Fast command | Broader command | Expected evidence |
| --- | --- | --- | --- |
| Contract |  |  |  |
| Product surface |  |  |  |
| Runtime/operations |  |  |  |

## Active Migration and Retirement Gates

| Old path or behavior | Replacement | Current state | Deletion condition | Owner | Target |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | YYYY-MM-DD |

## Current Work Routes

| Topic | Canonical work item or decision | Status |
| --- | --- | --- |
|  |  |  |

Root TODO/progress snapshots may link here, but unique detail belongs in the
canonical artifact named above.

## Index Maintenance

Update this file when module ownership, code boundaries, canonical paths,
status, dependencies, or validation commands change. Do not copy narrative
from the destination artifacts.
