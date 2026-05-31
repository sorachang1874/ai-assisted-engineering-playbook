# Pre-Manual Signoff

Run this before asking a human to manually test a feature.

## Build and Runtime

- [ ] Correct runtime mode selected.
- [ ] Database/schema is isolated.
- [ ] Object storage prefix is isolated.
- [ ] Provider keys and budgets are explicit.
- [ ] No local-only fallback is enabled.

## Contract Preflight

- [ ] Field owner matrix passes.
- [ ] Public endpoints agree on shared fields.
- [ ] Command registry is complete.
- [ ] Migration bridges are zero or explicitly tolerated.
- [ ] Fake provider contract matches live response shape.

## User Flow

- [ ] Core page loads.
- [ ] In-flight state is coherent.
- [ ] Terminal state is coherent.
- [ ] Error state is useful.
- [ ] UI does not expose internal contract/debug wording.

## Metrics

- [ ] Latency within expected range.
- [ ] Retry count explainable.
- [ ] No hidden fallback usage.
- [ ] No orphaned command/activity.

## Result

- Decision:
- Evidence:
- Follow-up:

