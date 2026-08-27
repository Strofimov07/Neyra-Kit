---
name: long-job-discipline
description: >-
  Makes long-running work survive deploys and restarts: run it outside the
  request/deploy unit, claim work atomically, heartbeat, resume from a cursor,
  and declare irreversible steps before they run. Use when adding or operating a
  backfill, migration job, reindex, batch import, or any multi-hour task.
when_to_use: >-
  Use when work runs longer than a request, continues after a response, or
  rewrites a large data set — including one-off operational backfills.
tools: Read, Grep, Glob, Bash
---

# Long job discipline

## Goal

A job measured in hours must outlive the things that restart in minutes. The
common loss is not a crash — it is a routine deploy killing an unattended job
that had no way to resume.

The runtime recipe (how a job is launched and where) is a **project fact**: keep
it in `settings/facts/` in the consuming repo.

## Protocol

### 1. Run it outside the unit that gets redeployed

- A job attached to the application process or an interactive shell in the app
  container dies with the next deploy or disconnect. Give it its own process or
  container, from the same image.
- Web workers are for requests. A job that outlives a request does not belong in
  one.

**Success criteria**
- The job's lifetime is independent of the app's deploy and of any session.

### 2. Claim work atomically

- Use a durable queue where a worker claims an item in a single conditional
  update. Two workers must not be able to hold the same item.
- In-memory status is not status: with more than one process it is per-process,
  and it disappears on restart.

**Success criteria**
- Claiming is atomic and status lives in durable storage.

### 3. Heartbeat and reclaim

- Workers heartbeat while processing; items whose heartbeat goes stale are
  reclaimed. Without this, a killed worker holds its item forever.

**Success criteria**
- A stale claim is reclaimed automatically, and this was exercised.

### 4. Make progress durable and the work idempotent

- Persist a cursor so a restart resumes where it stopped instead of from zero.
- Re-processing an item must be safe: the same item twice produces the same
  result, not duplicates or double charges.

**Success criteria**
- The job was killed mid-run and resumed correctly at least once.

### 5. Declare irreversible steps before running them

- A full reload that drops derived state (enrichment, computed fields, manual
  corrections) is destructive even though it is called a refresh. Name what will
  be lost, confirm it is reproducible, and take a snapshot first.

**Success criteria**
- Irreversible steps are named and gated, or shown to be reproducible.

### 6. Detect silent partial loss

- Bulk writers routinely report success while dropping a subset. Compare counts
  in versus counts persisted and fail loudly on a gap.

**Success criteria**
- A count reconciliation runs at the end of the job and can fail it.

### 7. Account for entitlements at both ends

- If the job consumes a user's quota or credit, charge it on enqueue and return
  it on failure. A crash mid-run must not silently keep the charge.

**Success criteria**
- Quota is restored on failure, verified by a killed run.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's a one-off, I'll just exec it in the app container." | One-offs get killed by the next deploy, hours in. Give it its own process (step 1). |
| "Nobody will deploy while it runs." | Somebody will, including CI. Design for it, don't coordinate around it. |
| "The status endpoint shows progress." | With several processes that status is per-process and lost on restart. Persist it (step 2). |
| "It's idempotent enough." | "Enough" means duplicates on the retry path. Prove it by re-running an item (step 4). |
| "The reload just rebuilds the data." | Reloads drop derived state that was expensive to compute. Name it first (step 5). |
| "The bulk write returned OK." | Bulk APIs report success with dropped items. Reconcile counts (step 6). |

## Output

- Where the job runs and why it survives a deploy.
- Claim, heartbeat, cursor, and idempotency mechanics, each stated concretely.
- The irreversible steps, their gate, and the snapshot taken.
- The count reconciliation result and the quota path on failure.
