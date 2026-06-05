# Prompt and Model-Output Contracts

When a system depends on a language or generative model, the prompt and the shape of the
model's output are production contracts, not loose strings. Treat them with the same
discipline as any other shared semantic: versioned, owned, validated, and recorded.

## Prompts Are Versioned Artifacts

A prompt template that affects user-visible behavior should be a named, versioned artifact
(for example `summary_v3`), not an inline literal edited in place.

Each prompt version should define:

- Owner and purpose.
- Input variables and where they come from.
- Output schema it is expected to produce.
- Safety/constraint clauses.
- Fallback behavior when the model fails the contract.

Editing a prompt is a contract change. Bump the version; do not silently mutate a live one.

## Output Is Validated, Not Trusted

Model output should be validated against an explicit schema before any consumer uses it.
On validation failure, fall back deterministically — do not pass malformed or unexpected
output downstream.

- Define the output schema in the shared contract layer, next to other shared types.
- Validate at the boundary (the gateway/adapter), not in every consumer.
- A schema miss is a handled case with a fallback, not an exception that reaches the user.

## Negative Capability Flags

Model output and agent-generated artifacts should say what they do not prove.
This is especially important when an artifact is later consumed by another
agent, evaluator, queue, or publication step.

Useful flags include:

- `user_facing_output_allowed`
- `publication_allowed`
- `external_requests_allowed`
- `cache_writes_allowed`
- `profile_mutation_allowed`
- `scheduling_allowed`

Default these to false. Promotion requires a separate gate and validation
evidence. This prevents a planning artifact or model summary from being
mistaken for execution evidence or publication approval.

## Records Enable Review, Comparison, and Rollback

Prompt/output handling fits the same append-only, auditable model as events: keep records
so behavior can be reviewed and reversed.

- Log prompt version, inputs (redacted), raw output, and the post-validation result.
- Because versions are explicit, you can compare two versions on the same inputs.
- Because output is recorded, you can roll back to a prior prompt version with evidence.

## Regression Evaluation

A change to a prompt or model can regress quality without failing any type check. Keep a
small, stable evaluation set per prompt contract:

- Representative inputs with expected properties (not necessarily exact strings).
- Run the eval before promoting a new prompt version.
- Treat a regression on the eval set the same as a failing test.

Batch evaluation belongs in an offline tools tier, separate from the live request path.

## What Stays Flexible

Provider choice, routing order, and token/cost budgets are useful abstractions but should
stay tunable, not frozen contracts. What callers depend on is the **capability interface
and the output schema** — not which provider answered or how many tokens it cost.
