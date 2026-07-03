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
