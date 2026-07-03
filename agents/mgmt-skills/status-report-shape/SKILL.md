---
name: status-report-shape
description: >-
  Shared rendering mechanic for every recurring management report: exec
  summary, RAG rollup, metrics table, risks, ranked improvement hypotheses
  with owners, and a self-eval section that grades last cycle's hypotheses
  against what actually happened. Used by team-health-check, delivery-audit,
  and portfolio-pmo — one shape, structurally consistent across cycles.
when_to_use: >-
  Use when producing any recurring health/status/portfolio digest that will be
  re-read next cycle. Not user-invoked directly in most cases — the other
  mgmt-skills call it as their output stage.
---

# Status report shape

## Goal

Every recurring management report has the same skeleton, so readers compare
cycles instead of re-learning formats — and the report grades its own past
hypotheses before making new ones.

## Input contract

- Metrics arrive through the connector ladder (see `settings/CONNECTORS.md` in
  the consuming workspace): **paste/CSV first, file second, MCP last**. A
  missing connector never blocks the report — degrade to manual input and say
  so in the report header.
- Each metric needs: name, current value, prior value (or n/a), threshold or
  target, and source. No threshold → the metric renders grey (unratable), not
  invented.

## Protocol

### 1. Classify

- Rate each metric 🟢/🟡/🔴 against its stated threshold; add a trend arrow
  (↑/→/↓) vs prior cycle. Unratable metrics stay grey with a one-line reason.

**Success criteria**
- Every metric has a rating + trend or an explicit "unratable because X".

### 2. Self-eval before new hypotheses

- Pull the prior report's hypotheses. Grade each: confirmed / refuted /
  unclear, with the observed metric movement as evidence.
- The self-eval section renders BEFORE new hypotheses — the reader sees the
  track record first.

**Success criteria**
- No new hypothesis is written until every prior one has a verdict.

### 3. Hypothesize per red/yellow zone

- For each 🟡/🔴 metric: 2–3 ranked hypotheses, each with an owner and a
  proposed experiment/next step. Hypotheses, not verdicts — phrased
  falsifiably ("if we X, metric Y moves by Z within N weeks").

**Success criteria**
- Every 🟡/🔴 zone has ranked, owned, falsifiable hypotheses.

### 4. Render the fixed sections

1. **Executive summary** — 3–5 sentences, business language, worst news first.
2. **Overall status** — one 🟢/🟡/🔴 + the single biggest driver.
3. **Key metrics table** — metric / current / prior / trend / rating / source.
4. **Self-eval** — prior hypotheses with verdicts.
5. **Risks & issues** — what could invalidate the picture.
6. **Hypotheses & next steps** — from step 3, with owners.

**Success criteria**
- All six sections present, in this order, every cycle.

## Rules

- **No individual performance ratings — ever.** Team-level rollups only.
  Activity metrics (commits, review counts, velocity) never rank people; a
  single-metric "productivity score" is a named antipattern (SPACE, GitClear
  2025). Person-level data belongs in the private goal-okr personal mode, not
  in any report this skill renders.
- Numbers come from the input contract, never from memory. A metric without a
  source line does not render.
- The self-eval section is mandatory — a report that only looks forward is
  marketing, not management.
- Same section order every cycle; additions go inside sections, never as new
  top-level sections mid-quarter.

## Non-goals

Collecting the metrics (the calling skill + connectors do that) and deciding
org changes (the reader does that — this skill produces hypotheses, not
decisions).

## Verification

The rendered report has all six sections; every prior hypothesis has a
verdict; every 🟡/🔴 has owned hypotheses; no person-level ranking anywhere.
