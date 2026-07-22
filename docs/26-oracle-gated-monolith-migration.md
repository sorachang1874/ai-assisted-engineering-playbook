# Oracle-Gated Monolith Migration

Distilled 2026-07-22 (second backflow batch, same refactor continuation as
doc 25): how to move code out of a mega-function that an entire production
system runs through — in this case a ~2,100-line recovery tick whose ordered
phase sequence, per-phase observables, and summary mapping are pinned
byte-identically by a characterization suite — without ever betting the
migration on your own reading comprehension.

## 1. The oracle is the contract, not the tests you write later

Before touching a monolith band, pin its CURRENT observable behavior with a
characterization suite that fails on ANY drift: ordering, owners, skip
reasons, summary keys, budget epilogues. Two properties make it an oracle
rather than a test:

- **Byte-identical assertions.** Not "roughly the same summary" — the exact
  record stream. Every migration slice must reproduce it exactly; a diff is a
  stop-the-line event, never something to "update the expectation" for.
- **Mutation-verified.** Before trusting it, prove the oracle catches
  reordering, gate-flips, and dropped summary slots. An oracle that cannot
  fail is decoration.

The oracle's authority must be socially absolute: the migration NEVER edits
it. If a slice cannot reproduce the records, the slice is redesigned.

## 2. The three-step slice ladder

Monolith bands resist extraction because of threaded state: locals written by
one region and consumed by a later one, plus closures capturing everything.
Do not move bodies first. Order the work so each step is separately
verifiable and behavior-invisible by construction:

1. **State lift.** Promote the cross-region threaded locals into named fields
   on an explicit context object. Choose ONLY state the oracle does not
   observe (it never appears in the pinned records) — then the lift cannot
   change observable behavior, and the oracle run is a pure confirmation.
   Measure first: in our case the documented "impossible threading" had
   already shrunk from many nonlocals to two, plus a handful of `*_this_tick`
   locals — re-measuring dissolved a stale impossibility claim.
2. **Closure promotion.** Move helper closures to module-level pure
   functions, verbatim. Purity must be verified against the WHOLE body — see
   §3 for how this failed us. Respect import direction: if the destination
   module cannot import the source, replicate trivial utilities locally with
   a comment rather than inverting the dependency.
3. **Verbatim body moves.** Only now move region bodies into registry-driven
   units, with the context object replacing the threaded locals. The only
   permitted transform is the local→context-field rewrite; anything else is
   redesign, which goes back through review.

Each step is its own commit gated by the full oracle + the surrounding
suites + every ratchet. Small steps are not caution theater: they localize
the inevitable failure to one mechanism.

## 3. Case: the oracle catching a partial-reading purity assessment

During closure promotion we classified a 100-line merge closure as pure after
reading its first 56 lines. Its tail referenced a sibling closure. The
promoted copy raised NameError deep inside the tick — and the oracle went
0/10 on the very next run, before the commit. The fix was to promote the real
dependency too (which WAS pure). Two lessons that generalize:

- **Purity is a whole-body property.** Scan the complete body for helper
  references mechanically (grep for call patterns), never assess by reading
  a prefix. Reading comprehension does not scale to 100-line closures at
  hour ten of a session.
- **The oracle converts a production landmine into a one-cycle fix.**
  Without it, that NameError lived inside a swallowed-exception recovery
  path and would have surfaced as silently-missing durable work in
  production ticks.

## 4. Interlocks with the ratchet family (doc 25)

Migration and debt-fencing compound: every module extracted from the
monolith enters the type-checker's allowlist at zero budget, so the
monolith's error budget dies with the monolith; the line-count/regrowth
ratchet prevents new feature work from re-inflating the donor while the
migration runs (we measured +8.4k lines of regrowth in five weeks when no
ratchet guarded the freeze — a boundary decision without an enforcement
mechanism is a wish). Sequence note: land the fences BEFORE the migration
batches, or you will be re-litigating the same regrowth at every slice.
