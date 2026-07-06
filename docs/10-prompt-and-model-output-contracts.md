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

## Review Verdicts Are Model Outputs Too

A gate's verdict is itself a model output, so it gets the same contract discipline as any other —
recursively (principle 31). A verdict accepted by regex anywhere in any comment ("looks like a
GO") is forgeable three ways: by accident (a reviewer musing "this isn't a GO yet"), by stale
copy-paste (yesterday's GO re-posted against today's diff), and by prompt injection (the diff
under review contains the very string the parser scans for). Because the verdict often *is* the
enforcement — the merge gate reads it — it fails closed: no compliant marker means do-not-merge
(principle 20, applied to the recursive case where the component *is* the enforcement).

### Minimal marker spec

A merge-authoritative verdict comment MUST carry all of:

- **SHA-bound.** An HTML marker binding the verdict to the exact reviewed commit:
  `<!-- REVIEW-VERDICT gate=<gate-id> sha=<full-40-hex-of-reviewed-HEAD> -->`. The gate re-reads
  current HEAD and rejects the verdict if the SHA does not match — a verdict is about one specific
  tree, never "the PR" in general.
- **Machine verdict marker, anchored to the last line.** The decision is the **last non-empty
  line**, matched anchored, not scanned from the body: `REVIEW-VERDICT: GO` |
  `REVIEW-VERDICT: GO-WITH-FIXES` | `REVIEW-VERDICT: NO-GO`. Anchoring is what stops a verdict word
  elsewhere in the prose from being read as the decision.
- **Nonce-fenced untrusted data.** Any content quoted from the change under review (diff hunks,
  logs, the author's own text) is fenced with a per-review random nonce
  (`<<<UNTRUSTED-{nonce}>>> … <<<END-UNTRUSTED-{nonce}>>>`); the parser ignores any marker found
  inside the fence. Injected text cannot forge a marker whose nonce it cannot predict.
- **Identity-restricted poster.** Only the designated reviewer identity (the gate's bot account,
  or a signed commit status) emits a merge-authoritative verdict; a verdict-shaped comment from any
  other identity is advisory text, not a gate result.
- **Fail-closed parse.** Any comment that is not exactly compliant — missing marker, unmatched
  SHA, verdict not on the anchored last line, wrong poster — resolves to **NON-COMPLIANT ⇒
  do-not-merge**, never to a permissive default.

A conforming verdict comment is in `examples/cross-review-verdict-example.md`.

### Must-reject fixtures

The verdict parser ships with fixtures it must reject — the recursive form of "output is
validated, not trusted":

- **Verdict quoted in prose** — "I'd call this a GO once the tests pass," with no anchored
  last-line marker ⇒ reject (no decision was emitted).
- **Stale SHA** — a well-formed `GO` whose marker SHA is an earlier commit than current HEAD ⇒
  reject (the approval is for a tree that no longer exists).
- **Truncated diff** — a verdict whose covered-range/diff digest does not match the full diff
  under review ⇒ reject (the reviewer did not see all of it).
- **Missing marker** — a thorough, plausible review carrying no `REVIEW-VERDICT` marker at all ⇒
  reject, fail-closed (do-not-merge), not "probably fine."
