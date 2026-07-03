---
name: team-health-check
description: >-
  Recurring engineering-org health report for a senior manager: delivery
  (DORA), effectiveness (SPACE-lite, team-level only), team morale (squad
  health self-assessment), infra cost trend, reliability/security signals —
  rendered via status-report-shape with trends, analysis, and improvement
  hypotheses. Weekly pulse + monthly deep report.
when_to_use: >-
  Use when the user asks for a team/org health check, an engineering status
  report for leadership, "how is the team doing", or on the registered
  weekly/monthly reporting routine.
---

# Team health check

## Goal

One recurring, structurally stable answer to "how healthy is the engineering
org" — grounded in named frameworks, honest about missing data, and always
ending in owned improvement hypotheses, not vibes.

## Metric families

Start with the families the workspace has connectors for (see
`settings/CONNECTORS.md`); paste-input any family the user asks for anyway.
Never block on a missing source — report the gap.

1. **Delivery — DORA 4+1**: deployment frequency, lead time for changes,
   change failure rate, time to restore, reliability. Source: CI/CD + VCS.
2. **Effectiveness — SPACE-lite, team-level**: cycle time by stage
   (coding / pickup / review / deploy — the bottleneck finder), review load
   distribution, satisfaction via the cheapest honest channel available
   (👍👎 + freetext in chat beats an unrun survey). Never person-ranked.
3. **Morale — squad health check**: team self-assessment, traffic-light per
   dimension (release ease, tech quality, value, speed, mission, fun,
   learning, support) + trend arrows. The team rates itself; the manager
   reads trends, not absolutes.
4. **Infra cost**: total + trend + top movers. Source: cloud billing export.
5. **Reliability/security**: incidents by severity, MTTR, open critical
   vulnerabilities, age of oldest critical.

## Protocol

### 1. Establish scope and window

- Which teams/streams, which period, pulse (weekly, families 1+5 only) or
  deep (monthly, all wired families). Confirm once, then keep stable.

**Success criteria**
- Scope + window stated in the report header, identical structure to prior cycle.

### 2. Collect through the connector ladder

- Per family: MCP if wired, else file, else ask for a paste. Record the source
  per metric; missing family → grey row with "no source yet", never silent.

**Success criteria**
- Every rendered number has a source; every missing family is visible.

### 3. Render via `status-report-shape`

- Full six-section shape; hypotheses per 🟡/🔴 family; self-eval of last
  cycle's hypotheses first.

**Success criteria**
- status-report-shape verification passes.

### 4. Deliver and file

- Deliver as the workspace prefers (page and/or email digest). File follow-up
  actions as tracker issues with owners — a hypothesis nobody owns in the
  tracker died in the report.

**Success criteria**
- Report delivered on the agreed surface; each hypothesis-owner pair exists
  as a tracked issue or has an explicit "not filed because" line.

## Rules

- Team-level only; the no-individual-ratings rule from `status-report-shape`
  applies with no exceptions here — this report reaches leadership.
- Trends over absolutes: a 🔴 improving beats a 🟢 decaying; say which is which.
- Frameworks are named (DORA / SPACE / squad-health) so readers can audit the
  method, not just the numbers.
- One new metric family per cycle at most — a report that doubles its metrics
  every cycle stops being comparable.

## Non-goals

Individual performance management (goal-okr personal mode, private), incident
response itself (incident-runbook), and fixing what the report finds.

## Verification

Report renders with ≥1 metric family fully sourced, all six shape sections,
self-eval verdicts on prior hypotheses, and zero person-level rankings.
