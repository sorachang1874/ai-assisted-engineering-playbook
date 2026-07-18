# Documentation Router

This file routes problems to canonical module documentation. It is an index,
not a source of contract or implementation detail.

## Route Metadata

| Field | Value |
| --- | --- |
| Owner |  |
| Last route audit | YYYY-MM-DD |
| Next route audit | YYYY-MM-DD |
| Link check | `python scripts/check_markdown_links.py` |
| Migration/retirement registry | `docs/governance/documentation-migrations.md` |

## Problem Routing

| Problem or change | Owning module | Module index | First artifact class | Validation entrypoint |
| --- | --- | --- | --- | --- |
| Shared field, API, event, command, or permission |  | `docs/modules/<module>/README.md` | `contracts/` |  |
| User flow, copy, or prototype |  | `docs/modules/<module>/README.md` | `product/` |  |
| Test failure or coverage |  | `docs/modules/<module>/README.md` | `testing/` |  |
| Incident, deploy, repair, or recovery |  | `docs/modules/<module>/README.md` | `operations/` |  |
| Migration or old-path retirement |  | `docs/modules/<module>/README.md` | `migrations/` |  |

## Module Routes

| Module | Responsibility | Code boundary | Owner | Module index | Status |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  | `docs/modules/<module>/README.md` | active |

Status values: `proposed`, `active`, `migrating`, `superseded`, `archived`.

## Project-Level Routes

Use these only for subjects that cannot have one module owner.

| Artifact class | Canonical location | Owner | Read when |
| --- | --- | --- | --- |
| Architecture | `docs/project/architecture/` |  |  |
| Contracts | `docs/project/contracts/` |  |  |
| Product | `docs/project/product/` |  |  |
| Testing | `docs/project/testing/` |  |  |
| Operations | `docs/project/operations/` |  |  |
| Decisions | `docs/project/decisions/` |  |  |

## Current Snapshots

| Snapshot | Purpose | Must link to |
| --- | --- | --- |
| `NEXT_TODO.md` | Current, blocked, and immediately next work | Canonical module work items and deletion gates |
| `PROGRESS.md` | Current state and latest handoff window | Durable evidence, decisions, and resume instructions |

## Routing Gaps

| Gap | Impact | Temporary route | Owner | Resolution target | Status |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  | YYYY-MM-DD | open |

Do not resolve a gap by copying detailed content into this index. Choose a
canonical owner and path, then link to it.
