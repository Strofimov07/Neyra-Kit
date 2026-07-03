---
name: skill-capture
description: >-
  Captures a repeatable engineering workflow as a reusable skill in the canonical
  dev skill catalog. Use when a process repeats, the user asks to institutionalize
  a workflow, or a useful execution pattern keeps reappearing.
when_to_use: >-
  Use when a workflow should stop living only in chat history and become a
  reusable skill under agents/dev-skills with clear triggers, steps, and
  success criteria.
---

# Skill capture

## Goal

Convert a repeatable workflow into a lean, triggerable skill that improves future execution quality.

## Workflow

### 1. Capture the real workflow

- Identify:
  - trigger conditions
  - required context sources
  - ordered steps
  - artifacts and success criteria
  - hard rules and non-goals

**Success criteria**
- The workflow is specific enough that another agent could repeat it reliably.

### 2. Keep the skill lean

- Put only the workflow-critical instructions in `SKILL.md`.
- Move heavy references, scripts, or assets to bundled resources only when they add deterministic value.

**Success criteria**
- The skill is concise and high-signal.

### 3. Make invocation safe

- The description must say what the skill does and when to use it.
- Trigger conditions must be narrow enough to avoid accidental invocation.
- If the workflow is self-contained, mark it as a candidate for forked execution in runtimes that support it; otherwise keep it inline.

**Success criteria**
- Another runtime could discover and invoke the skill correctly.

### 4. Pressure-test that it changes behavior

- Before trusting the skill, run its target scenario **without** the skill under
  pressure (time pressure + sunk cost + "it's obvious") and record the exact
  rationalizations the agent uses to cut corners — the RED baseline.
- Write the skill to close *those specific* loopholes. For a skip-under-pressure
  failure, that means a "Common rationalizations" block (see `SKILL_CONTRACT.md`).
- Re-run with the skill and confirm the corner-cutting no longer happens.

**Success criteria**
- The skill demonstrably changes behavior on the scenario it was written for — not
  just documents an intention. If you didn't watch it fail without the skill, you
  don't yet know the skill teaches the right thing.

### 5. Sync the catalog

- Add the skill under `agents/dev-skills/`.
- Update sync paths when needed so the skill is actually discoverable.

**Success criteria**
- The skill exists in the canonical source and is not orphaned from the execution stack.
