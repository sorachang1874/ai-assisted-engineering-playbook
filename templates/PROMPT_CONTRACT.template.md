# Prompt Contract: <name>_v<version>

## Purpose

What this prompt is for and where its output is consumed.

## Owner

Who owns this prompt version and its eval set.

## Version

| Version | Date | Change | Status |
| --- | --- | --- | --- |
| v1 |  | initial |  |

Status: `draft` | `active` | `superseded`. Editing a live prompt = new version, not in-place mutation.

## Input Variables

| Variable | Source | Required | Notes |
| --- | --- | --- | --- |
|  |  |  |  |

## Output Schema

Define the expected output shape (link to the shared contract type). Output is validated
against this before any consumer uses it.

```
<schema or type reference>
```

## Safety Constraints

Constraint clauses included in the prompt (tone, no-go content, identity boundaries,
forbidden output such as code/URLs/PII). See safety-and-degradation.

## Fallback

What is returned when the model fails the contract (timeout, failure, schema miss, filtered).
Fallback is graceful for the user and recorded for the operator.

## Evaluation Set

| Input | Expected properties | Last result |
| --- | --- | --- |
|  |  |  |

Run before promoting a new version. A regression here blocks promotion.
