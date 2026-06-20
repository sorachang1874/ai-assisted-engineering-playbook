# Example: Operator Override Decision Flow

A generic walkthrough of the practices in
`docs/13-operator-decisions-and-evidence-integrity.md`. The scenario: an
enrichment pipeline found conflicts between unverified upstream claims and
reviewed facts, captured them in a fail-closed conflict review, and an
operator must now decide, per field, which value downstream consumers may
prefer — without rewriting any reviewed artifact.

## 1. Upstream Produces a Decision Surface

The conflict-review builder emits one template row per conflict. Each row
carries a content-hash reference computed over exactly the values in
dispute:

```json
{
  "schema_version": "override_template.v0",
  "conflict_ref": "sha256:<hash over {item_id, field, claim_value, fact_value}>",
  "item_id": "sha256:<item fingerprint>",
  "field": "country",
  "current_claim_value": "DE",
  "reviewed_fact_value": "FR",
  "allowed_operator_decisions": [
    "keep_reviewed_fact_internal",
    "suppress_field",
    "override_to_claim_value_requires_independent_review"
  ],
  "application_allowed": false,
  "requires_independent_review_before_application": true
}
```

## 2. Operator Authors a Decision File

The operator copies template rows and fills only human-authorable fields.
Note the two copy-pasteable bindings: the echoed values (verified later by
hash recomputation) and the upstream `generated_at` echo:

```json
{
  "schema_version": "override_decision.v0",
  "decision_id": "current-v1",
  "review_id": "current-v1",
  "review_generated_at": "2026-06-09T15:03:57+00:00",
  "conflict_ref": "sha256:<same as template>",
  "item_id": "sha256:<same as template>",
  "field": "country",
  "current_claim_value": "DE",
  "reviewed_fact_value": "FR",
  "requested_decision": "keep_reviewed_fact_internal",
  "decision_reason": "Reviewed fact wins internally; claim stays unused for this field.",
  "decided_by": "operator-local",
  "decided_at": "2026-06-10T08:30:00+00:00",
  "independent_review_ref": null
}
```

No hand-computed digests anywhere: an operator can author this file with a
text editor.

## 3. Independent Batch Review, Recorded and Pinned

An independent reviewer reviews the exact decision file and records an entry
in the tracked review index. The entry pins verdict, batch id, file digest,
and line-level item-decision pairing:

```markdown
## override-decisions-current-v1-batch-review

- Gate: Independent batch review of operator override decisions
- Verdict: `GO`
- Decision id: `current-v1`
- Decision file digest: `sha256:<digest of override_decisions.jsonl>`
- Approved decisions:
  - `sha256:<conflict-ref-1>` -> `keep_reviewed_fact_internal`
  - `sha256:<conflict-ref-2>` -> `keep_reviewed_fact_internal`
  - `sha256:<conflict-ref-3>` -> `suppress_field`
  - `sha256:<conflict-ref-4>` -> `keep_reviewed_fact_internal`
- Boundaries: internal-only; no publication, no user-facing labels, no
  upstream mutation.
```

If the operator edits the decision file after this review, the digest no
longer matches and the applier blocks.

## 4. Applier Verifies Everything Fail-Closed

Before writing anything, the applier checks (each failure -> global
`blocked`, zero applied rows, populated issue counts):

1. ids are safe path components;
2. upstream artifacts have the expected schema versions, safety boundaries,
   and a status that actually has something to decide;
3. the current validation status equals what the conflict review recorded
   (status drift check);
4. decision rows: enums, reason length cap, identity format, timestamp
   format and window, `review_generated_at` equality, id echoes against CLI
   args and template;
5. decisions join templates by `conflict_ref` with exact set equality;
6. recomputed `conflict_ref` from echoed values matches the template row;
7. the batch review entry exists, has the approving verdict, the batch id,
   the decision-file digest, and line-level pairing for every decision row;
8. dangerous decisions (claim over reviewed fact) carry a per-item review
   reference passing the same content checks;
9. input digests are recorded into the output summary; counts reconcile;
10. outputs pass the sensitive scan and respect overwrite refusal across all
    outputs, including the report.

## 5. Output Carries Its Own Integrity Evidence

```json
{
  "schema_version": "override_application_summary.v0",
  "status": "applied_internal_only",
  "batch_review_ref": "docs/reviews/review_index.md#override-decisions-current-v1-batch-review",
  "supersedes_application_ids": [],
  "source_digests": {
    "override_template_sha256": "...",
    "conflict_review_summary_sha256": "...",
    "validation_summary_sha256": "...",
    "override_decisions_sha256": "..."
  },
  "metrics": {
    "conflict_count": 4,
    "decided_conflict_count": 4,
    "undecided_conflict_count": 0
  },
  "boundaries": {
    "applies_operator_overrides": true,
    "changes_upstream_artifacts": false,
    "approves_user_facing_output": false
  }
}
```

Applied rows carry the decision outcome under a self-limiting name
(`operator_decided_value`, not `effective_value`) plus a pinned
`is_validated: false` flag, so no later consumer can grep its way into
treating a decision record as measured truth.

## 6. Consumer Verifies Before Interpreting

The readiness evaluator that consumes the summary:

- verifies **all** recorded source digests against the input files it
  actually consumed (checking only one creates silent staleness);
- verifies the applied-rows file exists with row count equal to
  `decided_conflict_count`;
- branches on a total matrix over (upstream status x application status x
  integrity result), with every inconsistent corner explicit;
- only degrades or maintains the existing interpretation: in the decided
  state it replaces the pending action text with maintenance text while
  keeping every existing score cap in force. A score lift would be its own
  gated change.

## 7. Rollback and Re-Decision

Rollback is deleting the application directory and regenerating downstream
views — nothing else was written. After any upstream regeneration, digests
and the `review_generated_at` echo fail, so a fresh decision file, a fresh
batch review, and a fresh application are required by construction.
