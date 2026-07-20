# Apify/Harvest Operations Runbook

Hard-won operational contract for Apify-based provider work (HarvestAPI
actors). Everything below was paid for at least once in production. Read it
BEFORE any Apify submission. Related: doc 22 (review-lane reliability and
quota walls) and the project's own `HARVESTAPI_PLAYBOOK.md` (product-side
request contract).

## 1. Verified actor input contracts (2026-07)

### `linkedin-company-employees` (roster member lists)

```json
{
  "profileScraperMode": "Short ($4 per 1k)",
  "companies": ["https://www.linkedin.com/company/<slug>/"],
  "takePages": 100,
  "maxItems": 2500,
  "locations": ["United States"],
  "functionIds": ["8"],
  "companyBatchMode": "all_at_once"
}
```

- Hard cap ≈ **2500 items per call**. Function sharding is the coverage
  mechanism when a function exceeds the cap; capped shards keep truncation
  evidence (`provider_cap_hit`) and must escalate to sub-shards
  (keyword/title subdivision INSIDE the function), never just re-run the
  same capped shape — re-running the same shape returns ≈97% identical
  items (measured: +80/2500 across three duplicate runs).
- **Shard filters are PLAIN single-function payloads.** Engineering =
  `functionIds ["8"]`, research = `functionIds ["24"]`, product =
  `functionIds ["19"]`. NEVER emit the root∖other form
  (`functionIds ["8","24"] + excludeFunctionIds ["24"]`): it is redundant
  for single-valued functions and drops dual-classified members from EVERY
  function shard. Remainder scopes are the only place excludes belong.
- Member items carry opaque `ACwA…` LinkedIn URLs, member-level fields
  (name/headline/currentPositions/location) — NOT full experience. Full
  experience is a separate profile-scraper stage.

### `linkedin-profile-scraper` (full profiles)

```json
{
  "urls": ["https://www.linkedin.com/in/<id-or-slug>", "..."],
  "profileScraperMode": "Profile details no email ($4 per 1k)",
  "findEmail": false
}
```

- Only two modes exist: `Profile details no email ($4 per 1k)` and
  `Profile details + email search ($10 per 1k)`. There is NO "Full" mode;
  the no-email mode already returns rich payloads (full `experience`,
  `education`, `skills`, `languages`, `publications`, …).
- **Batch sizing: 400–800 urls per run, 4–8 concurrent runs, slot free =
  fill immediately.** Do NOT shard into dozens of small batches (64×48 was
  a measured mistake — more run overhead, more failure surface, more
  console noise). A ~26-url run finishes in <1 min; a 400-url run in
  ~10 min; size for worker-communication cost vs single-run duration.
- Item `linkedinUrl` may be a RESOLVED SLUG even when the submitted url was
  an opaque `ACwA…` id. File/keying must handle both (see §3).

### `linkedin-profile-search` (seed/discovery lane)

- Used for former-member seeds and name search. Probes and escalations use
  the same payload identity for adoption; identical repeated probes within
  seconds are a process bug, not a feature.

## 2. Spend discipline (dedupe BEFORE dispatch)

Every submission answers these in order, with the numbers printed:

1. **Inventory first.** What datasets already exist for this exact query
   (queue summaries, console)? What is already downloaded and merged
   (`profile_fetched`, file presence, resolved-url index)? Compute the
   delta set and dry-run the count BEFORE spending.
2. **Paid datasets are receipts.** A succeeded run's dataset is readable
   for free. Salvage-collect and adopt before any re-fetch; re-fetch is
   justified ONLY by a semantics change (e.g. fixed params) or proven
   staleness — record which.
3. **Union, don't choose.** When multiple paid datasets cover the same
   scope, union-dedupe by stable identity (LinkedIn URL) and keep
   multi-source provenance. Duplicate capped runs add small free deltas.
4. **Idempotency on submission.** A client timeout may still create the
   job/run server-side. On timeout, QUERY FIRST before retrying. Duplicate
   jobs self-deadlocked a 4-slot provider limiter and triple-paid one
   roster in production.
5. **Killing the driver ≠ aborting runs.** Any driver must track its run
   ids and call `POST /v2/actor-runs/{id}/abort` on stop/error. Before
   killing a driver, list its runs and abort them. (Paid incident: a killed
   resume driver had already submitted 5×400 urls of duplicate fetches.)
6. **Cancel semantics are lossy today.** Cancelling a job does NOT release
   provider-limiter leases (manual PG cleanup:
   `DELETE FROM runtime_provider_limiter_leases WHERE lease_owner LIKE
   '<prefix>:<job_id>:%'`) and its queued workers may still execute later
   (a cancelled job submitted a third duplicate run an hour later). After
   every cancel, clean leases AND cancel/interrupt its workers.

## 3. Identity and merge rules

- Member datasets: opaque `ACwA…` urls. Profile items: resolved slug urls.
  NEVER join by raw url string.
- Merge order that worked at 3k scale (99%): direct resolved-url → exact
  (first,last) → OpenAI-currentPosition disambiguation → normalized
  (diacritics/parenthetical/CJK order) → last-token-of-surname variant.
  Same-name collisions inside one company (~0.7%) stay UNMERGED — a wrong
  merge is worse than a missing profile.
- Driver skip logic keys on the DOCUMENT's `profile_fetched` flag, never
  on `sha(url)` — resolved slugs make url-sha checks silently useless and
  cause full re-fetches.
- Union-dedupe key: LinkedIn URL when present; name+company only shard-
  scoped. Two different people must never merge cross-shard.

## 4. Pre-spend checklist

- [ ] Existing datasets for this query listed (console + queue summaries).
- [ ] Already-downloaded/merged set computed; delta printed (target > 0?).
- [ ] Payload params match the actor contract above (plain function ids;
      correct mode string; no invented fields).
- [ ] Batch plan: 400–800/run, 4–8 concurrent, slot-fill; no small shards.
- [ ] Run-id tracking + abort path wired into the driver.
- [ ] On any retry: query-first (jobs/datasets), no blind resubmit.
- [ ] Cancel path: leases + workers cleaned, not just the job row.
- [ ] Salvage adopted before fresh spend; union of paid sets done first.
