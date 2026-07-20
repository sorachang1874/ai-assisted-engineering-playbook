# Paid Provider API Spend Discipline

Generic operating rules for ANY paid provider API (search/scrape/enrichment
providers, LLM relays, metered data feeds). Project-specific actor/parameter
contracts do NOT belong here — keep those in the owning project (e.g. its own
provider playbook). Related: doc 22 (review-lane reliability and quota walls).

## 1. Dedupe before dispatch, with printed numbers

Every paid submission answers, in order and with counts printed:

1. **Inventory**: what paid artifacts already exist for this exact work
   (datasets, run receipts, queue summaries, previously downloaded files,
   per-record "done" flags in the document of truth)?
2. **Delta**: what remains genuinely unfetched/uncovered? Dry-run the delta
   count BEFORE spending. Zero delta = no submission, no exceptions.
3. **Salvage before fresh spend**: a succeeded provider run is a readable
   receipt. Adopt paid artifacts (download is usually free) and union them
   before considering any re-fetch. Re-fetch only for a semantics change or
   proven staleness — record which.
4. **Union, never choose**: multiple paid artifacts over the same scope get
   union-merged on a stable identity with multi-source provenance preserved,
   never silently replaced by the newest.

## 2. Idempotency and cancellation are YOUR problem

- **Client timeout ≠ not submitted.** A timed-out hosted call may still
  create the server-side job/run. On timeout: query first (list
  jobs/datasets for the target), retry only if absent. A blind retry
  double-paid an entire roster in production and self-deadlocked the
  provider limiter.
- **Killing the driver ≠ cancelling the work.** Paid runs keep executing
  after the driver dies. Every driver must track its run ids and call the
  provider's abort endpoint on stop/error. Before killing a driver, list
  its runs and abort them.
- **Cancel paths are usually lossy.** Assume a cancel does NOT clean up:
  concurrency leases, queued workers, in-flight runs, and downstream
  watchers all need explicit cleanup. After every cancel, verify each of
  the four is actually dead (a cancelled job submitted a duplicate paid run
  an hour later via orphaned queued workers).
- **Long-lived runners are zombies waiting to happen.** A job whose
  supervisor dies must be detectable and adoptable; until that gate exists,
  supervise externally and record stale progress timestamps as alerts.

## 3. Identity bridging across provider stages

Providers routinely mint DIFFERENT identifiers at different stages (opaque
ids in a search/list result, canonical slugs/URLs in a detail fetch). Rules:

- Never join stages on a raw identifier string without a bridge.
- Build the join on stable identity with documented fallbacks (exact id →
  canonical form → attribute-backed match → name+scope), and let genuine
  collisions stay unmatched. A wrong merge corrupts every downstream stage;
  a missing merge is visible and retryable.
- Skip logic keys on the record-of-truth's done flag, never on a hash of an
  identifier that can have multiple valid forms. Hash-of-id skipping
  silently re-fetches everything once a second identifier form appears.

## 4. Batch geometry is a cost contract

- Size batches by the provider's real limits and unit economics (per-call
  caps, per-item charges, per-run overhead), not by habit. Many small runs
  multiply run overhead and failure surface; huge single runs concentrate
  failure loss. Record the sizing rule and its reasoning next to the driver.
- Slot-fill concurrency: a free worker slot dispatches immediately; no
  batch/tail special cases. Track per-run receipts (submitted ids, counts,
  status, dataset ids) so every spent cent is reconstructable.

## 5. Pre-spend checklist

- [ ] Paid artifacts for this scope listed; delta computed and printed.
- [ ] Salvage adopted and unioned before any fresh spend.
- [ ] Params validated against the OWNING project's provider contract doc
      (not from memory).
- [ ] Run-id tracking + abort path wired into the driver.
- [ ] Cancel/cleanup covers leases, workers, runs, watchers — verified dead.
- [ ] Skip logic keys on the done flag, not on identifier hashes.
- [ ] Every run leaves a durable receipt (ids, counts, status, dataset).
