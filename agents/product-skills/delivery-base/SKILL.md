---
name: delivery-base
description: >-
  Executes ecosystem work using repo governance: AGENTS.md precedence, Linear/Notion sync,
  role and task-anchor reporting, and mandatory quality gates. Use when planning or closing
  tasks, shipping features across Browser/Reader/backend, or when the user mentions Linear,
  Notion, acceptance criteria, Definition of Done, or delivery checklist.
---

# Delivery execution

## Source order

1. Stream-specific `agents/<stream>/AGENTS.md` when scope matches
2. Root `AGENTS.md`
3. `.cursor/rules/*.mdc`

If sources conflict, follow higher priority and state the assumption in the task summary.

## Every task-facing response (including final summary)

Include explicitly:

- **role sync:** `synced` / `assumed` (and brief active role set)
- **task anchor sync:** `synced` / `missing` / `not provided` (Linear or equivalent)

## Linear

- Moving a task into execution: **Todo → In Progress** when work actually starts
- **Done** only after verification evidence exists (tests, smoke path, or documented check)
- Do not invent product logic; prefer Linear acceptance criteria over guesses

## Notion (canonical product docs)

- Medium/large work: update Notion outcome in the **same cycle** as Linear status changes, especially when marking **Done**
- If Notion is unavailable: mark **`sync debt`** with owner/follow-up in the summary

## Quality gates (shipped features)

Verify the right subset per AGENTS.md **Mandatory Feature Quality Gates**: monitoring, dashboards, analytics events, tests, localization (for user-facing surfaces).

Fast path for tiny fixes still requires stating assumptions and residual risks.

## PR / completion summary format

- What changed / why / files / risks / follow-ups
- Documentation debt called out if registries or Notion could not be updated

## Memory bank

- Operational fallback only; not a replacement for Linear/Notion when those are available
