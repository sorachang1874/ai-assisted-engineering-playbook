# Review-Lane Reliability and Quota-Wall Operations

Doc 20 made multi-session teams schedulable; doc 21 made single-lane
interruption cheap. This doc is the next layer down: once five or six lanes
plus several independent reviews run in parallel, the *review channel itself*
becomes the flaky dependency, and account quota becomes a first-class failure
mode with its own runbook. All lessons below were paid for in one 24-hour
window on a production program (five fixed-forward lanes + six review lanes +
one live provider round).

## 1. The reviewer is an unreliable component — engineer for it

An independent review that dies mid-flight must fail closed (no evidence),
never produce a half-verdict you accidentally treat as a gate. Failure modes
observed, all real:

- **Mid-turn compaction forks the verdict.** A reviewer whose context
  overflows compacts and emits TWO different final answers (8,058 vs 8,753
  chars in our incident). A well-built gate rejects this
  (`final_response_item_exact` mismatch → INVALID artifact). Your brief must
  prevent it: *context budget is a hard constraint* — the pinned diff is
  provided; work from it plus targeted greps; NEVER read whole files
  (an 82k-line module in scope forces compaction).
- **Empty or incomplete scope pins are author-side P1s.** Two separate
  incidents: (a) `--base` equal to the implementation head produced an empty
  diff and a review finding "the pinned review scope is not valid for the
  claimed implementation"; (b) the scope omitted two files from the
  fixed-forward changeset, producing "the pinned review scope omits files
  that implement the fix". The rule: the review base is the commit BEFORE
  the implementation chain, and the file list is the union of the changeset —
  carry that exact list in the lane handoff so the rerun scope is copy-paste,
  not re-derived.
- **The reviewer's home state rots.** A long-lived reviewer home developed
  app-server protocol errors; two consecutive runs died while other homes
  worked. Cheap fix: one fresh minimal clone (config + auth + instructions
  only) per review lane, recreated on any transport failure.
- **Probe the channel before launching an expensive review.** A 15-second
  `POST /responses {model, "ping", max_output_tokens: 16}` against the relay
  would have saved three 40-minute doomed runs when the relay's subscription
  quota was exhausted.

## 2. Quota walls are a matrix, not an event

Three channels failed INDEPENDENTLY within hours, each with a different
signature, blast radius, and recovery owner:

| Channel | Signature | Frozen scope | Recovery |
| --- | --- | --- | --- |
| Agent platform subscription (Kimi/Codex plan) | `403 usage limit for this billing cycle` on subagent spawn | fixed-forward lanes | wait/upgrade; resume pattern |
| Model relay subscription (chshapi-style) | `insufficient_user_quota` mid-turn; reviews die with transport errors | independent reviews, model-backed planning, Luna-style live calls | recharge/rotate key; re-fire from the queue |
| Provider billing (HarvestAPI-class) | `platform-feature-disabled: monthly usage hard limit exceeded` | live acquisition | monthly refresh/rotate; salvage paid artifacts |

Operating rules:

1. **Keep every lane resume-ready at all times** (doc 21): uncommitted state
   in the lane worktree, handoff appended per round, BOARD card current. All
   three walls hit mid-lane; every lane resumed in minutes once its channel
   returned, with zero archaeology.
2. **Record the wall in the SSOT with the exact error text and first-hit
   timestamp.** Anyone (including future you) can then tell "lane is broken"
   from "channel is broke" in one glance, and no one re-fires doomed runs.
3. **Queue, don't drop.** Review lanes that fail on a channel wall go into an
   explicit re-fire queue with their prepared commands (base, scope, context
   text) — when the channel returns, re-firing is mechanical.
4. **Probe before spending** (see §1). Probe result decides whether the
   re-fire queue drains now or later.
5. **Never silently substitute channels.** A failed review channel is not
   permission to run the verdict through a different, unaudited path — the
   gate's independence and evidence rules still apply (doc 20: author ≠
   reviewer).

## 3. Live-path incident runbook (hosted workflow edition)

Four production incidents from one afternoon, each now a coded lesson:

- **Client timeout ≠ not-submitted.** A hosted `start-workflow` call that
  times out client-side may still create the job server-side. Two timeouts →
  three duplicate jobs → their shared provider-limiter leases (budget 4)
  deadlocked each other. Rule: submissions need idempotency keys; until the
  API has them, on timeout QUERY FIRST ("list jobs for this target company")
  before retrying.
- **Cancel does not release provider-limiter leases.** The two dead jobs'
  leases kept blocking until deleted manually. Manual repair procedure
  (local PG): inspect
  `SELECT lease_token, lease_owner, metadata_json FROM runtime_provider_limiter_leases`,
  delete rows whose owner job is cancelled/dead (`DELETE ... WHERE lease_owner
  LIKE '<prefix>:<job_id>:%'`), commit. Follow-up code fix: cancel/retry must
  release owned leases in the same pass.
- **Cancel's shared-service shutdown kills sibling runners.** Cancelling
  duplicate jobs requested a service shutdown that also killed the surviving
  job's runner, zombifying it (progress frozen, `job_not_runnable` on
  execute, recovery gate never adopts). Rule: recovery-side adoption must
  handle "runner killed, workers stale-queued" — detect, reset, re-drive;
  until it exists, `supervise-workflow --auto-job-daemon` manually.
- **Paid-but-uncollected provider artifacts are salvageable.** When the
  acquisition died after the provider run succeeded, the dataset id in the
  queue summary (`*_queue_summary.json`) is the receipt — downloading it
  costs nothing. Keep a salvage note in the lane card instead of re-paying.

## 4. Review-loop throughput at scale (what actually worked)

- **Resume-pattern lane owners.** Each fixed-forward lane keeps ONE agent
  identity across review rounds (resume with the new findings). Round N+1
  inherits the lane's full context: no re-briefing cost, and the owner knows
  which findings it already "fixed" inadequately — the main source of
  re-raises is the owner re-patching the same seam instead of the deeper
  owner-level cause. Brief that explicitly.
- **One integration owner, many authors.** All lanes commit on their own
  branch; the integration owner cherry-picks, re-validates on the shared
  branch, resolves cross-lane conflicts (two lanes hit `plan_review.py` in
  the same window — resolution kept both owners' semantics), and owns the
  self-hash-chain flips (digest regeneration after contract-prose edits)
  single-writer. Rebase each lane onto the integration head before its next
  round; the cherry-picked duplicates drop out of the rebase for free.
- **Reviews run parallel to development, gates stay on promotion edges.**
  Fixed-forward lanes proceed on the previous NO-GO's findings without
  waiting for the next verdict; promotion/live/signoff still requires the
  valid GO. This is the difference between "review as accelerator" and
  "review as blockage" (doc 20: the gate is an edge, not a queue).
- **Verdict archaeology is part of the loop.** Read every NO-GO for its
  classification column: `new` vs `re-raise` vs `residual`. A re-raise with
  new evidence means the previous fix patched the seam; a finding pinned at
  a pre-fix head is stale and must be marked, not re-fixed (one incident:
  a review pinned head predated the fix by two commits; the "finding" was
  already closed on the integration head).

## 5. Playbook/branch governance — one SSOT, merged often

This very repo accumulated three long-lived branches (`main`,
`distill/round-2-*`, `feat/principles-*`), which is the same failure the
coordination board exists to prevent: no single source of truth. Rules:

1. Exactly one integration branch (`main`); distill lanes are short-lived
   branches merged on landing, then deleted.
2. Each distill lands as ONE commit series with the doc + index link + any
   validator/script change (like the board-checker fix); never leave a doc
   unlinked from the README index.
3. Validators and scripts in the repo (packet checker, board checker,
   delivery-graph checker) get fixed in the same pass as the content that
   needs them — a validator bug discovered mid-use is a recording defect
   worth its own ledger entry.
4. If a branch must live longer than a week, it needs a merge date and an
   owner; otherwise it is archival, not active.

## Checklist

- [ ] Review brief caps context (pinned diff + targeted reads, never whole files).
- [ ] Review base = pre-implementation commit; scope = full changeset file list from the lane handoff.
- [ ] Channel probe passed within the last few minutes before any expensive review/run.
- [ ] Every lane is resume-ready (worktree state + handoff + BOARD card) right now.
- [ ] Quota-wall entry in the SSOT has exact error text + first-hit time + frozen scope + re-fire queue.
- [ ] No submission retries without query-first; idempotency key if the API supports it.
- [ ] Cancel path verified to release owned leases and not kill sibling runners.
- [ ] Paid provider artifacts recorded as salvageable receipts (dataset ids).
- [ ] Re-raised findings route to the owner-level cause, not the same seam.
- [ ] Exactly one integration branch; short-lived distill branches merged and deleted.
