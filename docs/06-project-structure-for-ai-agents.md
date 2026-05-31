# Project Structure for AI Agents

## Recommended Files

At the root:

- `AGENTS.md`: stable agent instructions.
- `README.md`: product and setup overview.
- `NEXT_TODO.md`: current roadmap, phase status, deletion gates.
- `PROGRESS.md`: recent progress and handoff summary.
- `docs/`: contracts, runtime modes, testing, architecture.
- `scripts/`: repeatable developer and CI commands.
- `tests/`: unit, contract, integration, smoke.

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

