---
name: eval-baseline
description: >-
  Makes a quality, cost, or performance measurement comparable over time by
  declaring its baseline — code revision, dataset, model, and pricing — and by
  marking results incomparable when the instrument itself changed. Use before
  quoting any number as evidence that something improved or regressed.
when_to_use: >-
  Use when running or reporting an evaluation, benchmark, cost measurement, or
  A/B comparison, and whenever a diff changes the measuring code, dataset, or
  scoring formula.
tools: Read, Grep, Glob, Bash
---

# Eval baseline

## Goal

Keep measurements decision-grade. The expensive failure is not a bad number —
it is two numbers compared across a silently changed instrument, which reads as
a real improvement and redirects weeks of work.

Run commands, dataset locations, and thresholds are **project facts**: read them
from the consuming repo's kit config or `settings/facts/`. This skill owns the
discipline only.

## Protocol

### 1. Declare the baseline before measuring

Record, with the result: code revision, dataset (identity **and** size), model
and its version, pricing table if cost is involved, and the environment the run
executed against.

**Success criteria**
- The result carries all five, not a bare number.

### 2. Change one axis at a time

- Instrument, dataset, and subject are three different axes. Moving two at once
  produces a number that explains nothing.
- If a corpus reload or backfill happened between runs, that is a dataset change
  even if nobody edited the dataset file.

**Success criteria**
- Exactly one axis differs from the compared run, or the comparison is dropped.

### 3. Mark incomparability loudly

- When the measuring code, scoring formula, or pricing changed, previous numbers
  are **incomparable** — label them so at the point of reporting, and re-baseline.
- Never quietly restate an old number under a new formula. Either recompute the
  old run under the new instrument, or state that the series is cut here.

**Success criteria**
- Reports show a visible break in the series where the instrument changed.

### 4. Pin the cases that matter

- Known-good and known-bad cases are pinned with expected outcomes, so a run
  answers "did this specific thing break" and not only "is the average fine".
- Aggregates hide the regressions that a stakeholder will actually notice.

**Success criteria**
- The pinned set covers every defect previously found in production.

### 5. Report negative and null results the same way

- A run that shows no improvement is a result. Report it with the same baseline
  block, and do not re-run until it looks better.

**Success criteria**
- The reported number is the one the run produced, including when it is bad.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's the same metric name, so it's comparable." | The name is not the instrument. If the formula or dataset moved, the series is cut (step 3). |
| "I only fixed a bug in the scorer." | A scorer fix changes every historical number. Re-baseline and say so. |
| "The corpus grew, but that shouldn't matter." | Size is part of dataset identity — recall and cost both move with it (step 1). |
| "I'll re-run it later with the same settings." | Settings drift between runs is exactly what makes numbers unusable. Record them now. |
| "The average is up, ship it." | Averages mask the specific cases stakeholders check. Read the pins (step 4). |
| "This run looks wrong, let me re-run before reporting." | Re-running until a number looks right is selection, not measurement. Report it, then investigate. |

## Output

- The baseline block (revision, dataset + size, model, pricing, environment).
- The single axis that changed against the compared run.
- Pinned-case outcomes, separately from aggregates.
- An explicit comparability verdict: comparable, or series cut here and why.
