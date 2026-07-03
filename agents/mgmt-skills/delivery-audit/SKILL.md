---
name: delivery-audit
description: >-
  Period audit of what a team actually shipped, in business terms: investment
  distribution (feature / bug / tech-debt / KTLO / unplanned), diff-vs-ticket
  honesty check, cycle-time-by-stage bottleneck, business-value line per
  closed item, and tracker-hygiene violations — rendered via
  status-report-shape. Answers "чем команда занималась и зачем это бизнесу".
when_to_use: >-
  Use when the user asks what a team shipped in a period, wants a delivery
  review / sprint retro digest for leadership, questions where engineering
  time went, or on a monthly/quarterly audit routine.
---

# Delivery audit

## Goal

Turn a period of closed tickets and merged PRs into a leadership-readable
answer: what shipped, why it mattered, where time actually went, where the
process leaks — with the tickets' own claims verified against the code.

## Protocol

### 1. Pull the period's record

- Closed issues + merged PRs for the team/stream and window, from the tracker
  and VCS (connector ladder — see `settings/CONNECTORS.md`).

**Success criteria**
- The issue/PR set is complete for the window and listed with links.

### 2. Investment distribution

- Classify each item: new feature / bug / tech-debt / KTLO / unplanned.
  Compare against the workspace's stated targets (defaults if unset:
  ~60% new work, <30% KTLO — Swarmia/Jellyfish convention; record which).

**Success criteria**
- Every item classified; distribution vs target rendered as a chart/table.

### 3. Honesty check — diff vs claim

- For a sample (all, if small; else the largest N by diff size), read the
  actual diff and compare with the ticket's claimed category and project.
  Flag: category mismatch (ticket says feature, diff is 90% refactor),
  scope creep (diff touches surfaces the ticket never mentions), and
  project mismatch.

**Success criteria**
- Sample size stated; every mismatch cited with issue id + evidence.

### 4. Speed and bottleneck

- Cycle time by stage from tracker timestamps: open→started, started→review,
  review→merged, merged→deployed. Name the slowest stage and its trend —
  the bottleneck is a stage, not a person.
- **Size-normalized duration**: for each closed item, set actual duration
  (started→merged) against actual size (diff lines/files from step 3's data,
  plus the estimate/points if the tracker has one). Flag both outlier tails:
  - *long-and-small* (duration ≫ size) — usually hidden complexity, blocked
    time, unclear requirements, or review starvation; the finding names the
    ticket and the suspected process cause, never the assignee's speed;
  - *big-and-instant* (size ≫ duration) — usually rubber-stamped review or
    scope that skipped planning; verify against the review record.
- **Estimate calibration** (when estimates exist): actual-vs-estimate ratio
  per item and its period distribution — a systematic 2× miss is a planning
  finding for the next cycle, not a per-person one.

**Success criteria**
- Per-stage medians + trend; one named bottleneck stage.
- Duration-vs-size outliers listed with issue ids and a process hypothesis
  each; estimate-calibration distribution reported when estimates exist.

### 5. Business meaning

- One line per shipped theme (not per ticket): what it lets users/the
  business do now. Trace each theme to its project and, where wired, its
  OKR (`goal-okr`). Items with no traceable "why" go to the violations list.

**Success criteria**
- Every shipped theme has a business-value line and a project anchor.

### 6. Hygiene violations

- No-project issues, stale In Progress (> workspace threshold), Done without
  verification note, category/scope mismatches from step 3. This is
  `linear-router`'s rule set applied retrospectively.

**Success criteria**
- Violations listed with ids and owners; recurring offenders noted as a trend.

### 7. Render via `status-report-shape`

- Narrative "what shipped and why" per stream + distribution + bottleneck +
  violations; hypotheses per 🟡/🔴 (e.g. review-stage bottleneck → owned
  experiment); self-eval of last audit's hypotheses first.

**Success criteria**
- status-report-shape verification passes.

## Rules

- The audit measures the system, not the people: bottlenecks are stages,
  distribution is a team property. No per-person output — `status-report-shape`'s
  rule applies.
- Diff evidence beats ticket text; where they disagree, the diff wins and the
  mismatch is the finding.
- Value lines are written for a reader who doesn't know the codebase —
  business language, no module names.

## Non-goals

Planning the next period (delivery-planner / portfolio-pmo), fixing the
violations (file them), and code review of the diffs themselves.

## Verification

Audit renders with a complete item set, stated sample for the honesty check,
per-stage cycle times, business-value lines per theme, and a violations list
with owners.
