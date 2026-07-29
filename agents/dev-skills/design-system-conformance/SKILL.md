---
name: design-system-conformance
description: >-
  Reviews UI work for reuse of existing components, tokens, states, and
  interaction patterns instead of inventing new surface behavior.
when_to_use: >-
  Use when implementing or reviewing UI code, especially if design exists in
  Figma or the surface already has shipped patterns that should be preserved.
---

# Design system conformance

## Goal

Keep UI changes visually and behaviorally consistent with the surface.

## Checklist

### 1. Reuse first

- Check for existing components, tokens, and shipped interaction patterns before creating new UI structure.

**Success criteria**
- The change reuses the nearest valid pattern.

### 2. Check state behavior

- Review hover, focus, disabled, loading, empty, and error states where relevant.

**Success criteria**
- The UI behaves consistently across expected states.

### 3. Check token usage

- Verify typography, spacing, colors, depth, and motion follow the surface rules or design tokens.

**Success criteria**
- Styling is anchored in system choices, not ad hoc values.

### 4. Check surface fit

- Preserve the existing visual language for that product unless the task explicitly changes it.

**Success criteria**
- The diff looks native to the surface, not like imported generic UI.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's faster to build this component fresh than to hunt for an existing one." | A fresh component drifts from the surface and duplicates behavior. "Reuse first" — check existing components, tokens, and shipped patterns before creating new structure (step 1). |
| "It's just the default state — other states aren't in scope." | Hover, focus, disabled, loading, empty, and error states are where the surface visibly breaks (step 2). Review them; a missing empty/error state is a defect, not a detail. |
| "This one hex/spacing value is fine hardcoded." | One hardcoded value is the seed of divergence. Anchor styling in typography/spacing/color tokens, not ad hoc values (step 3). |
| "The task is about behavior — matching the visual language is optional." | Preserve the existing visual language unless the task explicitly changes it (step 4), or the diff reads as imported generic UI. Match the surface. |
