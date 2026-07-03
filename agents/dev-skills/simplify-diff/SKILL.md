---
name: simplify-diff
description: >-
  Reviews changed files for reuse, code quality, efficiency, and scope control,
  then simplifies the diff before finalizing. Use after implementation and before
  final verification.
when_to_use: >-
  Use when code was already changed and you need a cleanup pass focused on
  duplicate logic, weak abstractions, redundant state, over-complex UI code,
  or avoidable hot-path work.
---

# Simplify diff

## Goal

Reduce unnecessary complexity in the current diff without expanding scope.

## Review pass

### 1. Reuse review

- Search for existing helpers, shared components, constants, and utilities that
  can replace new bespoke logic.
- Remove copy-paste variants when a local shared abstraction already exists.

**Success criteria**
- No new utility exists where a proven local one already fits.

### 2. Quality review

- Remove redundant state and derived-value caches that do not need to exist.
- Collapse parameter sprawl when the change can fit an existing contract.
- Delete comments that explain obvious “what”; keep only non-obvious “why”.
- Check that user-facing strings still go through the existing localization path.
- Check that analytics or observability hooks were not silently bypassed.

**Success criteria**
- The diff does not introduce hacky glue code, obvious duplication, or hardcoded UX strings.

### 3. Efficiency review

- Remove repeated work in render loops, request paths, polling loops, or file operations.
- Add change-detection guards for recurring updates when nothing actually changed.
- Prefer direct operation + error handling over pre-check + operation when the pre-check adds no value.

**Success criteria**
- New code does not add avoidable repeated work or broad no-op updates.

### 4. Scope review

- Keep cleanup limited to files and logic already touched by the task.
- If a broader cleanup is justified, call it out as follow-up work instead of silently expanding the diff.

**Success criteria**
- The final diff is cleaner without becoming a side-quest refactor.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's clean enough." | "Enough" hides duplication and dead state the next reader inherits. Do the reuse pass. |
| "No time to simplify." | The complexity you skip becomes everyone's tax. It's part of the change, not extra. |
| "I'll simplify in a follow-up." | Follow-ups rarely happen; the diff ships as-is. Simplify now, within scope. |
| "More abstraction is better." | A new abstraction over a proven local one just adds surface. Reuse before inventing. |

## Output

Summarize:
- what was simplified
- what was intentionally left unchanged
- any remaining debt worth a follow-up issue
