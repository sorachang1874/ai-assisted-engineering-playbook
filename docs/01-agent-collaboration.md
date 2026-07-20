# AI Coding Agent Collaboration

## Context Files

Use repository-local instructions to keep agents aligned:

- `AGENTS.md`: stable rules, architecture constraints, commands, verification expectations.
- `docs/README.md`: problem-to-module router for canonical documentation.
- `NEXT_TODO.md`: bounded current/blocked/next snapshot with links to module
  work items, deletion gates, and known blockers.
- `PROGRESS.md`: bounded current-state and recent-handoff snapshot with links to
  durable decisions and validation evidence.
- Contract docs: source of truth for shared semantics.

Keep root instruction and snapshot files concise. Put detailed domain
contracts, product artifacts, testing guidance, and runbooks in module-owned
directories and route them through `docs/README.md` and module indexes. See
[Documentation Routing and Lifecycle](18-documentation-routing-and-lifecycle.md).

## Task Brief Format

Each agent task should define:

- Goal
- Non-goals
- Affected contracts
- Expected files or modules
- Validation commands
- Stop conditions
- Handoff output

See `templates/AGENT_TASK_BRIEF.template.md`.

## Phase and Gate Format

For work that spans more than one coherent change, keep a phase registry and
review packets:

- phase registry: current stage, decision enabled, non-decisions, evidence
  requirements, boundary flags, next artifact;
- design packet: contract, artifact chain, evidence class, validation plan;
- implementation packet: files changed, tests, generated artifacts, observed
  outputs, residual risks;
- adoption packet: proof that defaults, schedules, publication, or user-facing
  claims are allowed for the current artifact.

See `templates/PHASE_REGISTRY.template.yaml` and
`templates/REVIEW_PACKET.template.md`.

Treat packets as handoff artifacts. A future agent should be able to understand
why a phase is blocked or ready without reading the full chat history.

## Plan, Execute, Validate, Review

Use explicit operating modes for substantial work:

- Plan: name the decision, artifact chain, schemas, evidence class, boundaries,
  and review gate.
- Execute: implement the smallest coherent slice against the accepted plan.
- Validate: run targeted tests, contract checks, generated-artifact checks, and
  redaction scans.
- Analyze: compare the produced artifact with the decision it was meant to
  enable.
- Review: ask an independent reviewer to judge the named gate from a packet.
- Adopt: change defaults, schedules, publication, or user-facing claims only
  after the adoption gate allows it.

Do not use implementation success as a substitute for design acceptance, and do
not use design acceptance as permission to execute risky actions. Each loop
must say which decisions are enabled and which remain blocked.

## Multi-Agent Rules

Use parallel agents only when work is owner-bounded:

- One agent can own frontend implementation.
- One can own backend contract and API.
- One can own tests and preflight.
- One can own docs and migration notes.

Avoid multiple agents editing the same contract or schema unless one lead agent owns the merge.

For multi-step work, make those boundaries executable in a checked-in delivery
graph before dispatch. The graph declares dependency edges, exact write sets,
shared hotspots, validation, review, and promotion. A lane is ready only when
its dependencies are complete and its writes cannot race another ready lane.
Use `.coord/` only as the gitignored live projection of that durable graph.

See [Throughput-Oriented Delivery](19-throughput-oriented-delivery.md) and
[`DELIVERY_GRAPH.template.json`](../templates/DELIVERY_GRAPH.template.json).

## Handoff Rules

Every handoff should include:

- What changed
- What was validated
- What failed or was not run
- What required context or tooling could not be accessed
- Files touched
- Residual risks
- Next action

The next agent should be able to resume without relying on chat history. For
the in-flight version of this rule — WIP commits, a per-lane resume card, and
recovery from a session that dies mid-task — see
[Interruption-Safe Handoff and Session Resume](21-interruption-safe-handoff.md).

If a missing dependency blocks context acquisition or verification, record it as
a follow-up with the impacted artifact. Examples include missing browser
libraries, PDF extraction tools, OCR, CLI authentication, local provider fakes,
container runtimes, or system packages. The handoff should recommend whether to
install a workspace-level dependency, use a project-local fixture, or ask the
operator for a different input format.

## Prompting Agents

Good prompts ask agents to:

- Explore before editing.
- Search all usages of changed symbols.
- State the owner/source-of-truth impact.
- Add regression tests.
- Update docs.
- Report validation honestly.

Avoid prompts that ask for broad implementation without contracts, such as "make the workflow stable" or "fix all state bugs." Convert them into bounded contract and owner tasks.
