# Example: Preflight Matrix

| Preflight | What It Catches | Expected Runtime | Blocks |
| --- | --- | --- | --- |
| Contract owner registry | Missing owner/source-of-truth fields | seconds | PR |
| Endpoint parity | Shared fields drift across endpoints | seconds | PR |
| Command owner registry | Command type has no owner or retry policy | seconds | PR |
| Migration bridge audit | Hidden fallback or legacy writer used | seconds | PR/release |
| Provider fake contract | Fake provider response shape drift | seconds/minutes | workflow tests |
| Database schema parity | Local/test/prod schema mismatch | seconds | PR |
| Runtime mode audit | Live/prod/test config leakage | seconds | PR |
| Browser smoke readiness | Broken critical page | minutes | release |
| Nightly pressure | Recovery, latency, throughput, race behavior | long | release |

## Guideline

If a nightly failure reveals a basic contract issue, add a faster preflight before rerunning nightly.

