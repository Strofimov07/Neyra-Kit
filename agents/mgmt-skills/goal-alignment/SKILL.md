---
name: goal-alignment
description: >-
  Traces active and planned work to the goal set (Objectives/KRs) and
  estimates each item's expected effect on its goal: direct / enabling /
  KTLO / orphan classification, falsifiable impact estimates that later
  cycles must grade, coverage and starvation analysis, and re-prioritization
  recommendations ranked by expected impact per effort.
when_to_use: >-
  Use when checking whether the team's tasks actually serve the stated goals
  ("чем мы заняты vs куда целимся"), before committing a sprint/period plan,
  when a health check shows activity without goal progress, or on a periodic
  alignment review. Pairs with goal-okr (the goal set) and portfolio-pmo
  (the work set).
---

# Goal alignment

## Goal

Every unit of active work either traceably serves a goal, is honest
maintenance, or is flagged — and every traced item carries a falsifiable
estimate of the effect it should have on its KR, so alignment claims get
graded against reality instead of staying opinions.

## Protocol

### 1. Load both sides

- **Goals**: the OKR set from `goal-okr` (tracker/strategy anchors). No OKR
  set yet → degrade honestly: elicit the period's 1–3 top goals from the user
  in one question, or use tracker project targets as proto-goals — and say
  which mode the analysis ran in.
- **Work**: the scope's In Progress + planned items (sprint / project /
  team backlog window) from the tracker.

**Success criteria**
- Both sets listed with ids; the goal-source mode is stated.

### 2. Trace every work item

Classify each item's relationship to the goal set:

- **direct** — completing it moves a named KR (say which one);
- **enabling** — unblocks or is a precondition for a direct item (name it);
- **KTLO/maintenance** — keeps the system running; legitimate, budgeted
  (default target ≤30%, delivery-audit convention);
- **orphan** — no defensible trace to any goal or maintenance need.

The trace must survive a "why?" chain of at most two hops — a three-hop
story ("this refactor helps velocity which helps everything") is an orphan
with extra steps.

**Success criteria**
- Every item classified; every direct/enabling item names its KR/parent.

### 3. Estimate expected effect (falsifiable, gradeable)

For each **direct** item: which KR, expected direction and magnitude —
a number toward the target when defensible ("≈+15% of the remaining gap"),
else a magnitude class (S/M/L) with one line of rationale — plus confidence
(low/med/high) and the check: "after ship, KR X should move ~Z within N
weeks". No defensible estimate → mark "effect unknown" explicitly; an
unknown is honest, an invented number is not.

**These estimates are commitments to be graded**: the next alignment run
(and team-health-check's self-eval) compares shipped items' predicted vs
actual KR movement.

**Success criteria**
- Every direct item has an estimate-with-check or an explicit "effect unknown".

### 4. Coverage and gaps

- **Coverage**: share of active work (by item count; by estimate/points when
  available) that is direct+enabling vs KTLO vs orphan.
- **Starved goals**: Objectives/KRs with zero direct items — a goal nobody
  works toward is a decision pending, not a hope.
- **Over-investment**: KRs already pacing On Track (per goal-okr run-rate)
  that still absorb a large share of direct items.

**Success criteria**
- Coverage split rendered; starved and over-invested KRs named.

### 5. Recommend

- Rank direct items by expected impact per effort (estimate ÷ size class).
- Propose concrete swaps: "pause A (orphan/over-invested), pull B (starved
  KR, high estimate)" — at most 3, each falsifiable via the step-3 checks.
- Orphans → triage list (link to a goal / reclassify KTLO / stop), never
  silent deletion.

**Success criteria**
- ≤3 ranked swap recommendations, each tied to a step-3 check; orphan triage
  list with a proposed disposition per item.

### 6. Grade the previous run

- Pull the prior alignment run's estimates for items that shipped since:
  predicted vs actual KR movement → confirmed / refuted / unclear. Render
  BEFORE this run's new estimates (same discipline as status-report-shape's
  self-eval).
- First run: state "cycle #1 — nothing to grade yet".

**Success criteria**
- Every shipped prior estimate has a verdict; calibration drift (systematic
  over/under-estimation) is named when visible.

## Rules

- Trace ≤2 hops; longer chains are orphans.
- No invented numbers: magnitude class + rationale beats a fake percent;
  "effect unknown" is a valid, visible answer.
- KTLO is legitimate inside its budget — the finding is exceeding the budget
  or hiding product work under KTLO, not maintenance existing.
- Team-level only; items are traced, people are not rated
  (status-report-shape rule applies).
- Estimates logged with the run output so the next cycle can grade them —
  an ungradeable estimate doesn't count as one.
- Recommendations are proposals for the owner's decision — this skill never
  re-prioritizes the tracker itself.

## Non-goals

Setting or challenging the goals themselves (goal-okr), period delivery
audit (delivery-audit), cross-team dependency planning (portfolio-pmo), and
sprint capacity math (delivery-planner).

## Verification

Every scoped work item appears exactly once in the classification; every
direct item carries a gradeable estimate or explicit unknown; coverage
split + starved-goal list + ≤3 swaps present; prior-run estimates graded
when a prior run exists.
