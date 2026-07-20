# Paid Dispatch and Live-Ops Discipline

Agent-side operating rules for work that can SPEND: paid provider dispatches,
live-mode runs, and the manual ops actions around them. Doc 23 owns the
provider-side spend rules (dedupe, idempotency, identity bridging, batch
geometry); doc 22 owns quota walls and the salvage runbook. This doc owns the
agent behaviors that decide whether those rules ever get a chance to apply.
All lessons below were paid for in one two-day production session — one of
them with a duplicated ~$15 provider bill, others with hours of
phantom-green reconciliation. Project-specific parameter contracts stay in
the owning project; only the generalized rules live here.

## 1. "Cancelled locally" says nothing about what was paid

The dedupe-before-dispatch inventory (doc 23 §1) is incomplete if it only
covers LOCAL materialization. A job cancelled or killed locally may have
provider runs that succeeded and billed; the receipt (run id, dataset id)
usually sits in the local snapshot or queue summary the agent is already
looking at. Before concluding "nothing usable was paid, re-fire everything":

1. Resolve every run id in local receipts against the provider's REMOTE run
   history — status, charged counts, dataset ids.
2. Adopt and union what succeeded (download is usually free).
3. Compute the delta and dispatch only the delta, with the re-dispatch
   reason recorded (semantics change or proven staleness — never "the local
   dir looked empty").

Symmetric rule: an unauthorized duplicate batch NEVER becomes canonical
because it exists. Canonical is the artifact acquired under the approved
plan. A successor agent that finds a fresh duplicate and suggests "just use
the newer copy" is committing the same error as the agent that created it —
existence confers no legitimacy; reject it and incident-log it.

*Example, anonymized:* an agent inspected only the local asset store (59
records), concluded a ~2,300-person roster "was never fetched", and re-fired
10 paid runs. The morning job it distrusted had been cancelled locally — but
its main remote run had SUCCEEDED with the full roster charged, and the run
id sat in that snapshot's own queue file. The duplicate bill was ~$15; the
salvage path cost $0 and was one remote-status query away.

Rule:
- [ ] Every run id in local receipts resolved against remote run history
      BEFORE any "uncovered" conclusion; remote status printed.
- [ ] Delta computed over remote+local union; re-dispatch reason recorded.
- [ ] A duplicate batch found later is rejected and logged, never promoted
      to canonical.

## 2. An instruction's premise is part of the instruction

When observed state contradicts the PREMISE of an explicit operator
instruction, the correct move is STOP and surface the conflict — never
resolve it unilaterally by expanding scope, and paid scope least of all.
"I'll report the finding and proceed" fails when the report lands after the
spend. Doc 20's packet rule (discover an unleased path/cost → stop, write
the question, do not widen locally) is this rule's leased-work instance;
this is the general form, and it binds even when the agent is confident the
instruction was written on a wrong assumption — confidence is not authority.

*Example:* a directive said "only re-fire the former lane" — premised on the
current lane being complete. The agent believed the current lane missing,
decided the premise had changed, and immediately submitted the FULL paid
job; the operator learned of the premise conflict from the bill. The
required output was one stop-and-ask line: "directive premise conflict:
current lane appears unfetched remotely — confirm full re-fire or
salvage-first?" and zero submissions until answered.

Rule:
- [ ] A premise conflict is a stop-and-ask event: surface it, record it in
      the handoff/board, submit nothing paid until resolved.
- [ ] Scope expansion requires an explicit new directive; a premise that
      "must have changed" is not one.

## 3. Paid-intent drivers fail closed on the live-mode contract

A driver that CAN simulate must prove it is live before it spends, and every
artifact it emits must carry a marker only the real live path can stamp.
Otherwise a mis-configured run silently simulates and reports phantom
success — and the hours go into reconciling "results" that never happened.
This is doc 11's fail-closed-artifact rule applied to mode selection: mode
unset or unproven = no dispatch, not simulated-by-default. Fail-closed
defaults cost a minute when they trip wrongly; fail-open defaults spend
money and produce phantom-green runs when they trip wrongly.

*Example:* in one day, a fail-closed mode assertion stopped two dispatches
that would have burned paid quota against a simulated provider (config drift
had flipped the mode flag). In the same window, a "live" run without the
assertion produced simulated evidence indistinguishable from live at the
summary level — discovered only when downstream stages found no provider
receipts.

Rule:
- [ ] Driver asserts the live-mode contract (mode flag, provider endpoint,
      non-simulated evidence marker) BEFORE the first billable call; failure
      aborts, never downgrades.
- [ ] Simulated output is structurally unable to pass as live evidence
      (marker stamped only by the live path); summaries distinguish
      simulated/live explicitly (doc 08's dry-run-vs-evidence checklist).
- [ ] When a long-lived service drives the paid flow, the driver's preflight
      also asserts PROCESS VINTAGE: the serving process must postdate the
      last request-shaping code change (`ps -o lstart` vs. code mtime).
      Landed ≠ running — a contract change driven through a stale process
      executes the OLD request shapes (a per-function shard plan that went
      out as one broad query because the backend predated the change).
      Restart the service or drive via the library path; dry-run validates
      the working tree, never the resident process.

## 4. The second manual live-ops action becomes a committed adapter

Any live-ops action performed twice — a salvage download, an abort sweep, a
lease cleanup, a batch collection loop — becomes a committed, reviewable
script with a registry entry (owner, command, last-verified date). Ad-hoc
`/tmp` scripts are incident incubators: unversioned, invisible to the next
session, unreviewable by any gate, and dead with the machine. The SYMMETRIC
sin is rewriting an existing helper because you didn't search: before
writing anything, grep the repo and the ops registry for machinery that
already does it, and extend that instead.

*Example:* an ad-hoc `/tmp` collection loop became the de-facto production
path for a 67-candidate live batch; it worked, left no receipts contract,
and a later lane had to reverse-engineer it into a durable committed runner
— the follow-up existed only because the ad-hoc path was never promoted
after its first success.

Rule:
- [ ] Ops action used twice → committed script + registry entry in the same
      pass, not "after this run".
- [ ] Before writing a new helper: search the registry/scripts; extend the
      existing adapter; a duplicate helper is a defect on sight.

## 5. Paid parameters resolve from an explicit resolver, never text inference

A parameter that shapes a paid request is a contract field with the full
doc-02 ownership treatment: one canonical source, resolved by explicit code
over a registry, printed and validated pre-dispatch. NEVER derive it by
substring/keyword inference over prompt text, config prose, or request
strings — text inference silently narrows or widens paid scope, and the
failure mode is a VALID-looking, successfully billed run over the wrong
cohort.

*Example:* a parameter resolver that matched substrings in request text
selected the wrong function-classification id for a paid roster query — the
run succeeded, billed, and produced a small wrong-bucket cohort that was
mistaken for the real lane data until a human audited the payload.

Rule:
- [ ] Every paid parameter has a named resolver over a canonical registry
      source; no substring/keyword path to a paid value exists.
- [ ] The resolved payload is printed and checked against the owning
      contract doc pre-dispatch (doc 23's pre-spend checklist).

## 6. Stale-test retirement is part of the refactor

Tests pinned to an API the refactor removed rot in place — and they fail at
import/collection time, which takes the WHOLE test module down with them and
can make the suite look greener when the broken file is silently deselected
or its error attributed to "known broken". Retiring or porting them is part
of the refactor's definition of done, not a follow-up: the collected-test
count is a contract (doc 03), and an unexplained count drop is hidden
coverage loss.

*Example:* after a planning-module refactor, several pin-tests still
imported the removed module; collection errors took down whole test files,
and the real coverage loss stayed masked until someone diffed
collected-test counts against the pre-refactor baseline.

Rule:
- [ ] Refactor done = zero import/collection failures AND collected-test
      count diff explained line-by-line.
- [ ] Pin-tests to removed APIs are ported or deleted in the refactor's own
      changeset, with the reason recorded.

## Related

- `23-paid-provider-api-spend-discipline.md` — provider-side spend rules
  this doc's §1 inventory feeds.
- `22-review-lane-reliability-and-quota-walls.md` — quota-wall matrix,
  salvage runbook, live-path incident rules.
- `02-contract-first-development.md` — the owner-matrix treatment §5 assumes.
- `11-safety-and-degradation.md` — fail-closed artifacts §3 specializes.
- `20-multi-session-team-execution.md` — the leased-work instance of §2's
  stop-and-ask rule.
- `03-testing-strategy.md` — suite-as-contract §6 extends.
