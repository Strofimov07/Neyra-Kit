---
name: portfolio-pmo
description: >-
  Portfolio-level PMO for a senior manager: cross-team dependency graph from
  the tracker, RAID register (Risks / Assumptions / Issues / Dependencies)
  with dedup-then-decide, batch planning of parallelizable streams with a
  mid-flight dependency re-check, RAG portfolio rollup, and on-demand
  "what's important / where / who does what" answers.
when_to_use: >-
  Use when the user plans across two or more teams/projects, asks what blocks
  what, needs a portfolio status for leadership, wants a RAID review, or asks
  where a stream stands and who owns it.
---

# Portfolio PMO

## Goal

Cross-team delivery stays legible and unblocked: dependencies are explicit,
risks live in one deduplicated register, parallel work is batched deliberately
with a human gate, and "who does what, what's important now" is answerable
from the tracker in one pass.

## Protocol

### 1. Portfolio map

- Enumerate active projects/streams from the tracker with owner, target,
  status. For dependencies use issue links/blocks relations; where they're
  missing, infer candidates from shared surfaces (same module, same contract,
  same team) and mark them "inferred — confirm".

**Success criteria**
- Every active stream has owner + status; dependency edges typed
  (declared vs inferred).

### 2. RAID register — dedup-then-decide

- Risks / Assumptions / Issues / Dependencies live as tracker items with a
  `raid:*` label in the portfolio project — the tracker is the register, not
  a parallel doc (Linear-source-of-truth rule).
- Before adding an entry, search existing open RAID items. A semantic match →
  comment + rank-bump the existing entry, never a duplicate. New entries get:
  statement, owner, mitigation/next step, review-by date.

**Success criteria**
- No two open RAID entries describe the same underlying risk; every entry has
  an owner and a review-by date.

### 3. Batch planning with a mid-flight re-check

- Group independent-looking streams/tickets into parallel batches; state the
  independence assumption per batch explicitly.
- **Human gate:** present batches for approval before dispatch — the manager
  picks, the skill never launches a batch on its own.
- **Re-check on analysis:** the moment any stream's own analysis/spec pass
  surfaces a file, table, contract, or team also claimed by a sibling in the
  batch — pause the batch, surface the conflict, re-approve or re-cut. The
  pre-dispatch independence assumption expires when real analysis starts
  (same rule as parallel-lanes' BLOCKED-on-conflict).

**Success criteria**
- Batches carry written independence assumptions; conflicts pause the batch
  rather than being worked around locally.

### 4. Q&A on demand

- "What's important now / where is X / who does what" answers come from live
  tracker queries in the moment — cite issue ids and owners, never memory.
  If the tracker can't answer it, that's a hygiene finding (file it), not a
  reason to guess.

**Success criteria**
- Every answer cites live tracker items; unanswerable questions become
  hygiene issues.

### 5. Portfolio report

- RAG rollup per stream + RAID delta (new / escalated / closed since last
  cycle) + new blocking dependencies, rendered via `status-report-shape`
  (self-eval of prior hypotheses included).

**Success criteria**
- status-report-shape verification passes; RAID delta explicit.

## Rules

- The tracker is the single register — no shadow spreadsheets, no parallel
  RAID docs. What isn't in the tracker doesn't exist for the portfolio.
- Every stream and RAID entry has exactly one owner; "the team" is not an owner.
- Escalations name the decision needed and by when — a risk without a
  decision-request is a status line, not an escalation.
- Batch dispatch of actual implementation work hands off to delivery-planner /
  goal-mode with their own gates — this skill decides *what* runs in
  parallel, not *how* the code lands.

## Non-goals

Sprint-level task slicing inside one team (delivery-planner), goal grading
(goal-okr), and delivery execution itself.

## Verification

Dependency map typed, RAID register deduplicated with owners+dates, batches
carry written assumptions and a human approval, report passes the shape check.
