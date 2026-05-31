# Testing Playbook

## Test Layers

| Layer | Purpose | Command | Runtime Mode |
| --- | --- | --- | --- |
| Unit | Pure logic | `make test-unit` | local |
| Contract | Shared semantic drift | `make test-contract` | local/CI |
| Integration | Real dependencies/fakes | `make test-integration` | containerized |
| Smoke | Critical UI/API flows | `make test-smoke` | containerized |
| Live | Targeted provider validation | `make test-live` | live-budgeted |
| Nightly | Long-chain pressure/recovery | `make test-nightly` | containerized |

## Rules

- Unit tests should not require network.
- Contract tests should be fast enough to run before long workflow tests.
- Integration tests should use production-like dependencies when behavior matters.
- Live tests should be small, budgeted, and never required for every PR.
- Nightly tests validate stability, recovery, latency, and pressure.

## Provider Fake Contract

Provider fakes must cover:

- Submit
- Poll
- Fetch/download
- Webhook/callback if applicable
- Item-level failure
- Retry/rate limit
- Late result
- Malformed response

