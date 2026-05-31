# Secrets and Configuration

Credentials and runtime configuration are easy to get wrong in ways that are expensive
later: keys leak into clients or logs, and behavior diverges because config is inferred
from scattered environment variables.

## Secrets

- Keep secrets server-side. Never ship provider keys or credentials to a client/browser.
- Never commit real secrets. Commit a `*.example` template with keys but no values.
- Keep secrets out of logs and audit records — redact before writing.
- Isolate credentials per runtime mode (dev/scripted/live/production); do not reuse a
  production key in test paths.
- Prefer a managed secret store in production over plaintext environment files.

## Configuration

- Select runtime mode from one central config, not from arbitrary ad-hoc env vars spread
  across the codebase (see runtime-and-environment-isolation).
- Validate required config at startup and fail closed with a clear message, rather than
  silently defaulting into a wrong mode.
- Keep config that changes behavior (modes, budgets, feature toggles) separate from
  secrets (credentials), even if both arrive via the environment.

## Preflight

A fast check should confirm, before long tests or deploy:

- No secret values are present in committed files or client bundles.
- The intended runtime mode is selected and its required config is present.
- Test paths are not pointed at production credentials or data.
