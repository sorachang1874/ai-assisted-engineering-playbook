# Local Multi-Agent Coordination

This directory is a gitignored live channel for agents working on the same
machine. It is not durable project memory. Checked-in delivery graphs and
contracts remain authoritative.

## Files

```text
.coord/
  README.md
  BOARD.md                       # lead-owned live projection of delivery graph(s)
  status-<agent>.md              # each agent writes only its own file
  session-packets/<packet>.md    # immutable issued packet per independent session attempt
  handoffs/<lane-id>.md          # immutable handoff per completed attempt
  distill/<stamp>-<agent>.md     # append-only improvement candidates
  log/<number>-<agent>-<kind>.md # append-only questions, decisions, corrections
```

Add `.coord/` to the adopting repository's `.gitignore` before dispatch. For
related repositories, keep one `.coord/` per repo; a neutral integration board
links exact release-candidate commits rather than sharing mutable runtime files.

## Authority

1. Checked-in contracts and delivery graphs win over this directory.
2. Only the integration lead changes graph dependencies, write sets, hotspot
   ownership, or merge order.
3. `BOARD.md` mirrors live status; it cannot create permission absent from the
   graph.
4. Promote a normative decision to Git, then announce its commit in the log.
5. Cross-project work exchanges versioned capability/request/result/evidence
   envelopes and pinned commits, never dirty-tree paths or implicit files.
6. An issued session packet is immutable. Replace it with a higher packet
   version when its base, dependencies, path lease, or hotspot order changes.

## Start or Resume

1. Read repository instructions and the documentation router.
2. Read the checked-in delivery graph referenced by `BOARD.md`.
3. Validate it and list ready lanes:

   ```sh
   python scripts/check_delivery_graph.py <graph-path> --ready
   ```

4. Read `BOARD.md`, your own status, and logs newer than your last seen number.
5. Claim only a ready lane whose owner matches you. Record repo, commit,
   branch/worktree, expected completion, exact validation, and write paths.
6. For an independent Coding Agent session, validate its packet with
   `python scripts/check_session_packet.py <packet> --ready`, then verify the
   worktree `HEAD` equals the packet's full base commit.
7. Re-check the shared worktree before every edit. An unplanned writer in one
   of your paths is a stop condition.

## While Working

- Write only your lane's declared paths and your own `.coord` files.
- Never edit another agent's status or handoff.
- Keep your status file resumable by a cold, different-tool successor: goal,
  base commit, touched paths, last validation command and result, current
  state, and the exact next step. Commit WIP to your lane branch at every
  natural boundary — uncommitted progress is invisible to the lease, the
  board, and whoever resumes a lane whose session died mid-task.
- Append questions/corrections; do not rewrite published log entries.
- A contract-direction change, new write path, hotspot conflict, destructive
  operation, or premature cross-project call stops the lane and returns it to
  the lead.
- Capture repeatable inefficiency in `distill/` without interrupting the active
  lane or editing its files.

## Handoff

Write one handoff with lane id and graph commit, exact repository/files/commits,
commands and counts, deviations/new writes, review status, residuals,
fixed-forward recommendation, negative evidence, distill candidates, and the
next lane this output unblocks. For a cross-project boundary, also record exact
envelope versions and producer evidence digest.

The lead independently verifies the commit and changes the board. A worker does
not mark a promotion or integration lane complete.

## Lead Sweep

On a user ping, merge event, expected-done overrun, or scheduled sweep, the lead:

1. validates graphs and reads ready waves;
2. checks statuses, handoffs, branches/PRs, and new logs;
3. compares declared writes with actual diffs;
4. detects stale/conflicting claims and cross-repo state leakage;
5. retires or supersedes stale packets without editing claimed packets in place;
6. integrates completed lanes in graph and hotspot order;
7. creates fixed-forward lanes for scoped findings;
8. refreshes the board; and
9. schedules a distill lane when its trigger fires.

Archive completed rows and old logs after durable state is linked from the
project snapshot. Do not let `.coord/` become a second progress database.
