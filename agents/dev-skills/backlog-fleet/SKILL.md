---
name: backlog-fleet
description: >-
  Scans a tracker stream's open backlog, proposes parallelizable batches of
  pre-existing tickets with written independence assumptions, gets explicit
  human approval, and dispatches the batch across isolated lanes — with a
  mid-flight independence re-check that pauses the whole batch when a lane's
  own analysis contradicts the assumptions.
when_to_use: >-
  Use when the user asks to burn down a backlog in parallel ("разгреби бэклог
  параллельно", "batch these tickets", "fleet"). Opt-in orchestration — never
  auto-invoked. Not for one sweeping change (batch-migration) or one goal
  decomposed top-down (goal-mode); this starts from tickets that already exist.
---

# Backlog fleet

## Goal

Turn an existing backlog into parallel lanes deliberately: independence is a
written, approved assumption — and it expires the moment any lane's real
analysis contradicts it, pausing the batch instead of silently colliding.

## Protocol

### 1. Pull the candidate set

- Open issues for the named stream/project from the tracker (every issue has
  a project — linear-router rule). Respect explicit filters (priority, label,
  "only bugs"); state the set with ids before any grouping.

**Success criteria**
- Candidate list with ids/titles shown; filters applied are named.

### 2. Independence analysis → batch proposal

- For each candidate pair, look for shared surfaces: files/modules (grep the
  paths each ticket implies), schema/tables, contracts, and same-team human
  dependencies. Cheap static pass — its output is an **assumption**, not a
  proof, and is written down as such.
- Propose batches: parallel-safe sets + the ordered remainder (blocked-by
  chains run sequentially). Each batch carries its written independence
  assumptions ("A and B don't share X because Y").

**Success criteria**
- Every batch has explicit written assumptions; conflicted tickets are
  sequenced, not forced parallel.

### 3. CHECKPOINT — human approves the batch

- Present batches, assumptions, and lane count. **Nothing dispatches until
  the user picks a batch** (same posture as goal-mode checkpoint 1).

**Success criteria**
- Dispatch happens only for an explicitly approved batch.

### 4. Dispatch across lanes

- One ticket = one lane = one branch = one worktree (`parallel-lanes` —
  mandatory, not optional). Flip each ticket to In Progress on lane start
  (pr-hygiene step 1). Record BASE per lane (`subagent-dispatch` ledger).

**Success criteria**
- Lanes isolated per parallel-lanes; ledger reconstructable; statuses flipped.

### 5. Mid-flight independence re-check

- The pre-dispatch assumption **expires when real analysis starts**: the
  moment any lane's spec/analysis pass surfaces a file, table, or contract a
  sibling's scope claims — that lane reports `BLOCKED: dependency-conflict`
  and **the whole batch pauses** (not just that lane) until the user
  re-approves the grouping or re-cuts it.
- Re-approval outcomes: proceed (conflict is benign, stated why), serialize
  the two lanes, or re-cut the batch.

**Success criteria**
- A discovered overlap pauses the batch; no lane ever "works around" a
  conflict locally.

### 6. Integrate and close the loop

- Lanes land one at a time per parallel-lanes step 4 (review → merge →
  verify-runtime on the integrated surface → delete lane). Tickets flip to
  Done only after their gate. Batch retro: one `kit-evolution` pass over all
  lanes' signals, not one per lane.

**Success criteria**
- Each lane gated before integration; one consolidated retro; all ticket
  statuses truthful.

## Rules

- Opt-in only; the checkpoint is mandatory — no batch dispatches itself.
- Independence assumptions are written before dispatch and are falsifiable
  during it; "we checked at planning time" is not a defense mid-flight.
- One ticket per lane; a lane never adopts a sibling's scope to "help".
- The tracker is the task source; the dispatch ledger is ephemeral run-state.
- Caps inherit goal-mode's discipline: respect a stated lane cap (default 2,
  max 4); queue the rest.

## Common rationalizations — do not accept these

- "The overlap is small, I'll just handle it in my lane." The independence
  assumption is the user's approval basis — it expired; report BLOCKED.
- "Pausing the whole batch is wasteful." A silent semantic collision costs
  more than a pause; the user re-approves in one message.
- "These tickets are obviously independent, skip the write-up." Unwritten
  assumptions can't expire, can't be re-checked, can't be re-approved.

## Non-goals

Decomposing one goal (goal-mode), one sweeping mechanical change
(batch-migration), sprint capacity planning (delivery-planner), and the git
mechanics themselves (parallel-lanes owns those).

## Verification

The transcript shows: candidate set → written assumptions → explicit approval
→ isolated lanes with flipped statuses → (if any conflict) a batch pause with
re-approval → gated integration and one consolidated retro.
