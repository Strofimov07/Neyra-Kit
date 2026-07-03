---
name: migration-safety
description: >-
  Reviews database schema migrations for production safety: backward
  compatibility with the still-deployed app version, lock behavior on
  large/hot tables, and a rollback path. Fires whenever a diff adds, alters,
  or removes a model field, index, or migration file.
when_to_use: >-
  Use when the diff touches migrations/ or model field definitions (Django or
  equivalent ORM). Pairs with contract-safety (API surface) — this covers the
  schema layer contract-safety does not: lock behavior, expand/contract
  sequencing, rollback.
---

# Migration safety

## Goal

A migration that passes tests and code review can still take a full-table
lock on a hot table or break the previous app version mid-rollout. This gate
asks the three questions tests don't.

## Review

### 1. Classify the operation

- Add column / drop column / rename / index / type change / data migration —
  each has a different risk profile. Mixed migrations (schema + data in one)
  are a flag by themselves: split them.

**Success criteria**
- Every operation in the migration named with its risk class.

### 2. Backward compatibility — the rolling-deploy window

- During deploy, old code and new schema coexist. Will the still-deployed
  version read/write this table correctly mid-migration?
- Renames and drops are guilty until proven split into **expand/contract**:
  add new + dual-write/backfill + switch readers + drop old, each step its
  own deploy. A one-shot rename is a rollout breakage waiting for traffic.

**Success criteria**
- Explicit verdict: compatible / needs expand-contract split (with the split
  named) / accepted-risk with the reason stated.

### 3. Lock behavior on large/hot tables

- Flag operations that take an exclusive lock proportional to table size:
  non-concurrent index creation, `NOT NULL` without default on old Postgres
  semantics, type changes rewriting the table, `VACUUM FULL`-class moves.
- Table size unknown → ask or check; "probably small" is not a size.
- Risky + hot → require the safer equivalent (concurrent index, nullable +
  backfill + constraint) or an explicit maintenance-window call-out.

**Success criteria**
- Each lock-taking operation has: table size (or an explicit unknown→ask),
  lock class, and either a safer path or a stated window.

### 4. Rollback path

- Can this migration be reversed? Destructive ops (dropped column/table,
  lossy type change) can't — that requires an explicit line: "data loss on
  rollback accepted by <owner>", not silence.
- Data migrations: is the reverse a no-op, a restore, or impossible? Say which.

**Success criteria**
- A named rollback path, or a named owner accepting that there isn't one.

### 5. Report

- Same shape as contract-safety: changed schema surface → compatibility
  verdict → lock risk table → rollback path → follow-up debt (e.g. "drop old
  column after release N+2" gets a tracker issue, not a memory).

**Success criteria**
- Deferred contract steps (the "contract" half of expand/contract) exist as
  tracker issues before the review closes.

## Common rationalizations — do not accept these

- **"It's a small table."** Size it or ask. Tables that were small get hot;
  the lock class doesn't care about your recollection.
- **"We'll run it off-hours anyway."** An unstated window is not a plan —
  name the window in the review or use the safe variant.
- **"The ORM generated it, it's standard."** The ORM optimizes for
  correctness, not for lock behavior on your data volume.
- **"We can always roll back."** Not after a drop. Rollback claims require a
  path, not confidence.

## Non-goals

API/contract compatibility (contract-safety), query performance tuning, and
executing the migration.

## Verification

The review output contains: per-operation risk class, a rolling-deploy
compatibility verdict, lock analysis with table sizes (or explicit unknowns),
a rollback line, and filed follow-ups for deferred contract steps.
