# Documentation Routing and Lifecycle

Documentation is a routing layer for engineers and coding agents, not a flat
archive of everything a project has learned. A reader should be able to start
from a problem, identify the owning module, and reach the canonical contract,
product definition, test guidance, or operator runbook without searching the
whole repository.

This chapter defines a module-first documentation structure, the routing
contract for Markdown indexes, and a retirement lifecycle that prevents root
`TODO` and `PROGRESS` files from growing without bound.

## Routing Contract

Use a three-hop route:

1. The root `AGENTS.md` and `README.md` point to `docs/README.md`.
2. `docs/README.md` classifies the problem and points to the owning module
   index.
3. Each module index points to the canonical artifact for the question.

The route is an index, not another source of truth. It names paths, owners,
status, and read conditions; it does not copy contract or implementation detail
from the destination document.

Every route must answer:

- Which module owns this problem?
- Which code paths and user surfaces are in that module?
- Which document is canonical for this artifact type?
- Is that document active, migrating, superseded, archived, or proposed?
- Which validation command detects drift?
- Where should a routing gap or stale document be recorded?

Use relative Markdown links for real routes so the link checker can verify the
graph. Use unlinked backtick paths only for illustrative placeholders.

## Recommended Directory Layout

Organize durable documents by module first, then by artifact type:

```text
AGENTS.md
README.md
NEXT_TODO.md                 # bounded current/next snapshot
PROGRESS.md                  # bounded recent handoff snapshot
docs/
  README.md                  # project documentation router
  project/                   # genuinely cross-module material
    architecture/
    contracts/
    product/
    operations/
    testing/
    decisions/
  modules/
    <module>/
      README.md              # module router
      contracts/
      product/
      architecture/
      testing/
      operations/
      migrations/
      decisions/
      archive/
  governance/
    documentation-migrations.md
    documentation-retirement.md
  archive/                   # retired project-level material
```

Not every directory must exist on day one. Create a category when its first
canonical artifact appears. Empty directory scaffolding creates noise without
improving routing.

Use `docs/project/` only when one module cannot own the subject. A public field
used by three modules may have a project-level owner matrix; the detailed
producer and consumer behavior still belongs in each affected module and links
back to the shared contract.

Contracts, product prototypes, test plans, and runbooks for one module should
not share a flat folder. Their different review triggers, audiences, and
lifecycles are easier to preserve when their paths express both the module and
artifact class.

## Problem-to-Document Routing

The project router should contain a table equivalent to this one, adapted to
the repository:

| Problem or change | First route | Then read | Expected validation |
| --- | --- | --- | --- |
| Shared field, state, API, command, event, or permission | Owning module index | `contracts/` and linked owner matrix | contract preflight plus targeted tests |
| User flow, copy, interaction, or prototype | Owning module index | `product/` and linked public contract | product acceptance or UI contract checks |
| Module boundary or dependency direction | Owning module index | `architecture/` and linked decision records | dependency or architecture checks |
| Test failure or coverage change | Owning module index | `testing/`, then the named contract | targeted test, then broader affected suite |
| Incident, deploy, repair, retry, or recovery | Owning module index | `operations/`, then runtime contracts | runbook preflight or realistic recovery path |
| Storage or compatibility cutover | Owning module index | `migrations/`, contract, and deletion gate | migration checks and old-path usage check |
| Cross-module rule | Project router | `project/`, then every named module index | cross-module contract preflight |
| Current work or recent handoff | Root snapshot | linked module work item or decision | commands recorded in the linked artifact |
| Unknown ownership | Project router routing-gaps table | code owners and call-site search | add the decided route in the same change |

This classification narrows documentation discovery; it never replaces code
reference searches. An agent changing a shared symbol must still search its
producers and consumers after reaching the correct contract.

## Project Router Convention

Create `docs/README.md` from
[`DOCS_INDEX.template.md`](../templates/DOCS_INDEX.template.md). Keep it short
enough to scan in one pass. It should contain:

- the problem-to-module route table;
- module names, code boundaries, owners, and module-index links;
- project-level document categories and their owners;
- the location of current snapshots and the migration/retirement registry;
- routing gaps that have an owner and resolution target;
- the last route audit date and the command used to validate links.

Do not place design rationale, status narratives, or copied contract fields in
the router. If a row needs a paragraph to explain its destination, the
destination is probably missing a focused artifact.

## Module Router Convention

Create each `docs/modules/<module>/README.md` from
[`MODULE_INDEX.template.md`](../templates/MODULE_INDEX.template.md). A module
router should name:

- the module's responsibility and non-responsibilities;
- code entry points and public surfaces;
- canonical contracts, product artifacts, architecture decisions, testing
  guidance, operations runbooks, migrations, and retired material;
- upstream and downstream modules;
- targeted validation commands;
- active migration or deletion gates;
- the owner and last verification date for the index.

One artifact has one canonical path. Multiple indexes may link to it, but must
not maintain competing summaries of its normative content. If two modules
co-own a contract, choose one project-level canonical contract and list the
producer/consumer responsibilities in its owner matrix.

## Artifact Metadata

Durable module documents should begin with a compact metadata block or table:

| Field | Meaning |
| --- | --- |
| Status | `proposed`, `active`, `migrating`, `superseded`, or `archived` |
| Owner | Person or team accountable for correctness |
| Module | Owning module or `project` |
| Canonical path | Path that indexes should link to |
| Last verified | Date the content was checked against code or product behavior |
| Review triggers | Changes that require this document to be re-read or updated |
| Supersedes / superseded by | Explicit replacement link when applicable |
| Retirement condition | Deletion or archive condition for temporary material |

Do not add metadata that nobody maintains. These fields exist because each is
used for routing, review, or retirement.

## Root TODO and Progress Files Are Snapshots

`NEXT_TODO.md` and `PROGRESS.md` are project-level entry points. They are useful
because agents can find them immediately; they become harmful when used as an
append-only project database.

`NEXT_TODO.md` should contain only:

- the current objective;
- active, blocked, and immediately next work;
- links to canonical module work items, contracts, decisions, and deletion
  gates;
- project-wide validation gates relevant to that current work;
- snapshot owner, refresh date, next cleanup date, and size budget.

`PROGRESS.md` should contain only:

- current shipped or verified state;
- recent changes needed for the next handoff;
- links to durable module evidence and decisions;
- open risks and exact resume instructions;
- snapshot owner, refresh date, next cleanup date, and size budget.

Move detailed backlog items to the owning module, durable decisions to decision
records, contract semantics to contract documents, and completed evidence to
review or release artifacts. Replace stale snapshot rows instead of appending a
new account beneath them.

Each repository should set explicit budgets. A practical starting policy is:

- refresh both snapshots at every milestone boundary and at least weekly while
  active work continues;
- retain only current, blocked, and next items in `NEXT_TODO.md`;
- retain only the latest handoff window in `PROGRESS.md`;
- review either file when it exceeds 200 lines or its stated next-cleanup date;
- move durable content before trimming, then delete duplicated narrative.

The line threshold is a trigger for review, not an invitation to compress
important facts into unreadable prose. A project may choose a different number,
but it must record one.

## Document Lifecycle

Use explicit state transitions:

```text
proposed -> active -> migrating -> superseded -> archived -> deleted
                  \---------------------------> archived
```

- `proposed`: not yet authoritative; adoption decision is still open.
- `active`: canonical for its named scope.
- `migrating`: still needed while readers or behavior move to a replacement.
- `superseded`: no longer canonical; contains a forward link and no unresolved
  unique content.
- `archived`: retained only for audit or historical evidence and excluded from
  normal agent context.
- `deleted`: removed after retention, legal, audit, and backlink conditions are
  satisfied.

An active document must not link to an archived document as its only source of
current behavior. An archived document must clearly say that it is non-canonical
and link forward when a replacement exists.

Track moves and retirements in
`docs/governance/documentation-migrations.md` (or the repository's equivalent)
with:

| Old path | Canonical replacement | State | Backlinks checked | Content gap | Owner | Delete/archive condition | Target date |
| --- | --- | --- | --- | --- | --- | --- | --- |

Keep redirects or stub indexes only when external links or active branches need
them. Give every stub a deletion condition; otherwise a compatibility layer
quietly becomes permanent.

## Cleanup Loop

Run documentation cleanup at each milestone and on the project's stated
cadence:

1. Check every router link and every active module index.
2. Find active documents past their verification date.
3. Replace root snapshot history with links to durable module artifacts.
4. Identify duplicate canonical claims and choose one owner/path.
5. Move completed migrations to `superseded` or `archived`.
6. Check backlinks before deleting or moving a path.
7. Remove empty compatibility stubs whose deletion conditions passed.
8. Update route-audit dates and record residual gaps with owners.

At minimum, CI should fail on broken local Markdown links. Mature repositories
should also lint that:

- every module in the project router has a real module index;
- every active route has an owner and existing canonical path;
- no canonical path appears as active in more than one route row;
- snapshots stay within their declared size and refresh budgets;
- `superseded` documents name a replacement or a recorded no-replacement
  decision;
- retirement rows do not pass their target dates silently.

Prefer generating index inventories from a small registry once manual routing
tables become error-prone. The generated file must identify its source and CI
must regenerate-and-diff it.

## Agent Read and Update Protocol

When starting a task:

1. Read the applicable `AGENTS.md` files.
2. Open `docs/README.md` and classify the problem.
3. Open the owning module index.
4. Read only the artifact classes required by the task and their explicitly
   linked cross-module contracts.
5. Search code references for affected symbols and contracts.
6. If the route is missing or wrong, record and repair the routing gap as part
   of the same bounded change.

When completing a task:

1. Update the canonical module artifact if behavior, ownership, product intent,
   tests, operations, or migration status changed.
2. Update the module index only when a route, status, owner, or validation
   command changed.
3. Refresh root snapshots by replacing stale entries with current links.
4. Update the migration/retirement registry for moves, supersessions, or
   temporary compatibility paths.
5. Run link checks and targeted behavior validation.

Do not load every document "for context." The router is designed to make the
minimum sufficient context explicit and auditable.

## Phase-1 Adoption Without a Mass Move

Repositories with a large flat `docs/` directory should not start by moving
everything. A safe first phase is additive:

1. Inventory existing documents and group them by owning module and artifact
   class without changing paths.
2. Add `docs/README.md` and module indexes that link to the current canonical
   paths.
3. Add a documentation migration/retirement registry and record ambiguous or
   duplicate sources.
4. Mark `NEXT_TODO.md` and `PROGRESS.md` as bounded snapshots and replace newly
   discovered detail with links.
5. Route all new documents directly into the module-first structure.
6. Move old documents one module at a time only when backlinks, open branches,
   and review scope are understood.
7. Delete compatibility stubs only when their recorded conditions pass.

This preserves current links while making new work follow the intended
structure. It also turns mass reorganization into small, reviewable migrations
instead of a repository-wide rename that obscures semantic changes.

## Adoption Is Complete When

- a new agent can route a representative contract, product, test, and incident
  question from `docs/README.md` without repository-wide document search;
- every active module has an index, owner, code boundary, and validation route;
- each durable artifact has one canonical path and an explicit lifecycle state;
- root TODO/progress files contain snapshots and links, not unique historical
  detail;
- a migration/retirement registry accounts for legacy paths and duplicates;
- local Markdown links pass; and
- the cleanup cadence has an owner and next due date.
