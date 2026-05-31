# Safety and Degradation

This applies to any system that returns model-generated or otherwise untrusted content to
users. The goal is to keep unsafe or broken output from reaching a consumer while keeping
the system honest about when it degraded.

## Review on Both Sides

Check inputs and outputs, not just one:

- **Input review** — validate or screen user/agent input before it shapes a request.
- **Output review** — screen generated output before it reaches a consumer.

A failed check substitutes a safe response. It does not surface the raw rejection to the
end user, and it does not pass questionable content through.

## User-Invisible Fallback Must Stay Operator-Visible

A degraded or fallback response can be invisible to the end user — but its use must always
be visible to operators.

- Log every fallback/degradation with cause (timeout, failure, filtered, budget).
- Count it; expose it in metrics and preflight output.
- A rising fallback rate is an incident signal, not a quiet success.

This reconciles two rules that look opposed: "always give the user a graceful result" and
"no hidden fallback." The fallback is graceful for the user and recorded for the operator.
A fallback that no one can see is a silent normal path, which is exactly what to avoid.

## Incident Response

When unsafe or malformed output is caught (or escapes):

- Record the input, prompt/version, provider, and filter verdict.
- Reproduce offline, away from the live path.
- Tighten the filter or the prompt contract.
- Add a regression case before closing the incident.

## Make Safety a Contract

Treat the safety boundary like any other contract: owner, allowed/blocked conditions,
where it is enforced, what the fallback is, and a fast check that proves it is wired in.
Enforce it at one boundary (the gateway/adapter), not scattered across consumers.
