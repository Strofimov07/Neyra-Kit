---
name: goal-okr
description: >-
  Goal-setting and OKR tracking for a senior manager: forms OKRs from strategy
  and active projects, grades 0.0–1.0, computes expected-vs-actual run-rate
  with auto-status, challenges goals via a progress-vs-confidence protocol
  (both directions — sandbagging too), and keeps a private personal-goals mode
  for direct reports with hard trust gates.
when_to_use: >-
  Use when setting, updating, grading, or challenging OKRs/goals at any
  cadence; when translating strategy into measurable objectives; when the user
  asks for run-rate / pace-to-target on goals; or for private 1:1 goal work
  with a direct report (personal mode).
---

# Goal / OKR tracking

## Goal

Goals are falsifiable, anchored to strategy, paced against time, and
challenged in both directions — the skill refuses to record what skipped the
discipline, the same way goal-mode refuses to skip its checkpoints.

## Structure

- **Objective**: qualitative, ambitious, time-boxed. 2–4 **Key Results** each:
  measurable, graded 0.0–1.0 at cycle end (0.7–1.0 = success; a consistent
  1.0 is a planning smell, not a triumph).
- Every Objective anchors to a strategy item or tracker project — **no anchor,
  not created** (linear-router posture). KRs are written as falsifiable
  criteria via `spec-elicitation` (EARS form: measurable value, source, date).

## Protocol

### 1. Form (or import) the OKR set

- From strategy + active portfolio (`portfolio-pmo`'s map where available):
  draft Objectives, elicit KRs one question at a time until each is
  falsifiable — reject "improve X" without a number, source, and date.

**Success criteria**
- Every KR has value/source/date; every Objective has an anchor.

### 2. Check-in cycle

- Per KR: current value (from its stated source), **progress** (% toward
  target) and **confidence** (owner's 1–5 or low/med/high that the target
  lands) — captured separately; the divergence is the signal.
- **Run-rate**: expected progress = straight line from start to deadline.
  Auto-status from the gap (Viva-Goals convention): expected − actual > 25% →
  **At Risk**; 0–25% → **Behind**; ≤ 0 → **On Track**.

**Success criteria**
- Every KR update carries progress + confidence + computed status; no status
  is hand-assigned against the formula.

### 3. Challenge protocol — enforce-then-proceed

- Triggers: status At Risk/Behind, or progress and confidence diverging
  (high progress + falling confidence is a leading indicator, treat as a
  trigger), or a KR ≥0.8 for two consecutive cycles (**sandbagging check** —
  goal likely set too low; challenge upward, propose recalibration).
- On trigger, the update is **not recorded** until answered: what gets us
  back on track (or why recalibrate), who owns the next step, by when.
  Refusing to answer is a valid outcome — recorded as an explicit
  "unmitigated risk accepted by <name>", never as silence.

**Success criteria**
- No triggered KR update lands without the three answers or an explicit
  accepted-risk line; sandbagged KRs get a recalibration proposal.

### 4. Cycle review

- Quarter/period end: grade all KRs, name the misses AND the
  suspiciously-easy (both are calibration errors), carry/kill/recalibrate
  each Objective with a one-line reason. Render via `status-report-shape`
  (self-eval = last cycle's confidence calls vs actual grades).

**Success criteria**
- Every KR graded; every Objective has an explicit carry/kill/recalibrate
  decision; the calibration track record is rendered.

## Personal mode (direct reports) — private, hard-gated

Part of operational management: each direct report can hold 1–3 personal KRs
(linked to a team KR or a growth goal), same mechanics (run-rate, confidence,
challenge), 1:1 cadence. **Different trust tier, non-negotiable rules:**

- **Physical separation, not filtering**: personal-mode data lives only under
  `settings/private/` in the manager's workspace (gitignored, never installed,
  never published — see `settings/README.md`). It never appears in any
  team-level report this kit renders; `status-report-shape`'s
  no-individual-ratings rule is the other half of this boundary.
- **Candidate, never verdict**: if the trend heuristic fires (N cycles Off
  Track + falling confidence), the skill surfaces a *candidate with an
  evidence trail* (dated KR history) to the manager and stops. Whether this
  is a performance conversation is a human judgment — the skill never labels
  a person.
- **Draft-only outward**: improvement plans (SMART goals, 30/60/90
  checkpoints, dated fact log) are drafts for the manager to review with
  HR/legal — employment law varies by jurisdiction. The skill never sends,
  files, or writes anything about a person to any external system (HRIS,
  email, tracker) — `trust-boundary-review` applies as a mandatory pre-check,
  destructive tier.
- Works both directions: the same trend view flags "outgrown the role"
  (consistent overperformance + high confidence) as a growth/promotion
  conversation candidate.

## Rules

- No anchor → no Objective; no number/source/date → no KR. The skill refuses,
  it doesn't warn.
- Status comes from the formula; confidence comes from the owner; neither
  overwrites the other — divergence is information.
- Challenge goes both directions: Behind gets a recovery answer, sandbagged
  gets a recalibration proposal.
- Personal mode never mixes with team mode in one output, one file, or one
  conversation thread.

## Non-goals

Task decomposition and sprint planning (delivery-planner), portfolio
dependency management (portfolio-pmo), and any autonomous HR action —
personal mode drafts, a human decides.

## Verification

A vague KR is rejected with the elicitation questions shown; a triggered
update without answers does not land; run-rate statuses match the formula on
spot-check; personal-mode data exists only under `settings/private/`.
