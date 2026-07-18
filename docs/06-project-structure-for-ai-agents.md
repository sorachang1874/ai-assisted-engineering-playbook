# Project Structure for AI Agents

## Recommended Files

At the root:

- `AGENTS.md`: stable agent instructions.
- `README.md`: product and setup overview.
- `NEXT_TODO.md`: bounded current/blocked/next snapshot that links to module
  work items and deletion gates.
- `PROGRESS.md`: bounded current-state and recent-handoff snapshot that links to
  durable evidence.
- `docs/README.md`: problem-to-module documentation router.
- `docs/`: module-owned contracts, product artifacts, runtime modes, testing,
  architecture, operations, migrations, and decisions.
- `scripts/`: repeatable developer and CI commands.
- `tests/`: unit, contract, integration, smoke.
- `artifacts/` or `var/`: generated local outputs that are useful for review
  but not necessarily committed.

## Contract Docs

Keep one contract per meaningful domain:

- Workflow runtime
- Provider adapter
- Projection/read model
- Public API
- Export
- CRM or business state
- Asset/evidence/assertion
- Agent operation/action registry

Each contract should include owner matrices and preflight commands.

## Command Surface

Expose stable commands:

- `make test-unit`
- `make test-contract`
- `make test-integration`
- `make test-smoke`
- `make test-nightly`
- `make dev-doctor`
- `make dev-up`
- `make dev-down`

Agents perform better when commands are discoverable and documented.

## Directory Boundaries

Use directory-level `AGENTS.md` files only when a subtree has materially different rules. Avoid scattering contradictory instructions.

For large codebases, include lightweight module maps:

- Ownership
- Entry points
- Shared contracts
- Runtime modes
- Test commands
- Migration status

Prefer module-first document paths such as
`docs/modules/<module>/contracts/` and
`docs/modules/<module>/operations/` over a flat project-wide document folder.
Keep genuinely cross-module material under `docs/project/`, with one explicit
owner and links to each affected module.

Use root TODO/progress files as replaceable snapshots, not append-only stores.
Detailed work, contract, product, testing, and operational content belongs in
the owning module and is reached through the project and module indexes. See
[Documentation Routing and Lifecycle](18-documentation-routing-and-lifecycle.md)
and the copyable [`DOCS_INDEX`](../templates/DOCS_INDEX.template.md) and
[`MODULE_INDEX`](../templates/MODULE_INDEX.template.md) templates.

## Generated Artifact Boundaries

Generated outputs should be organized by purpose and evidence class, not dumped
into one flat folder. A useful pattern is:

- `artifacts/plans/`: plan-only outputs with execution flags false;
- `artifacts/reports/`: human-readable summaries generated from validated data;
- `artifacts/manifests/`: machine-readable inventories, digests, and source
  snapshots;
- `artifacts/private/`: local-only outputs that must not be published;
- `artifacts/tmp/`: disposable scratch output.

Document which generated paths are committed, ignored, scanned for secrets,
reviewed, or safe to publish. Do not let a report become user-facing just
because it is easy to render.
