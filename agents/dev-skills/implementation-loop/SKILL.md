---
name: implementation-loop
description: >-
  Executes coding tasks with a strict inspect -> plan -> patch -> verify loop,
  minimal diffs, explicit assumptions, and strong repo-pattern reuse. Use for
  most implementation work unless a narrower domain skill already covers the task.
when_to_use: >-
  Use when implementing a feature, bugfix, refactor, or product change in this
  repo and the main risk is speculative coding, over-scoped edits, or weak
  verification.
---

# Implementation loop

## Goal

Ship the smallest correct change that fits existing repo patterns and is verified
to the strongest practical level.

## Workflow

### 1. Inspect before editing

- Read the nearest implementation, adjacent call sites, and existing patterns.
- Check the highest-confidence product source available for the task:
  Linear -> Notion -> Figma -> code.
- Find the real integration points before proposing abstractions.

**Success criteria**
- Relevant files and existing patterns are identified.
- Product logic is grounded in a source or an explicit assumption.

### 2. Write a short plan

- State the target behavior, the minimal files to change, and the intended
  validation path.
- Name the non-goals so scope stays tight.

**Success criteria**
- The change can be described in a few concrete steps.
- Intentional non-goals are explicit.

### 3. Patch minimally

- Change only what is required for the requested outcome.
- Reuse existing utilities, components, and contracts before introducing new ones.
- Do not mix opportunistic cleanup with delivery unless correctness requires it.
- Keep business logic out of view code when the surface already follows that split.

**Success criteria**
- The diff is narrow and reviewable.
- New logic matches existing architectural boundaries.

### 4. Verify with the strongest practical checks

- Run the best available validation for the surface:
  - tests for business logic and contracts
  - real UI/browser flow for user-facing web changes
  - runtime/smoke path for integration changes
- If a check cannot run, say exactly what was blocked and what remains unverified.

**Success criteria**
- Verification status is explicit.
- Residual risk is named, not implied.

### 5. Summarize for engineering use

- Report:
  - what changed
  - why it changed
  - intentional non-goals
  - completed verification
  - missing verification or risks

**Success criteria**
- Another engineer can review the change and understand scope and confidence quickly.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "I'll inspect as I go." | Coding before reading local patterns produces noisy, off-pattern diffs. Inspect first. |
| "A quick refactor while I'm here." | Opportunistic cleanup mixed with delivery wrecks scope and review. Defer it to a follow-up. |
| "The source of truth is missing — I'll guess the behavior." | Guessed product behavior ships wrong. State the assumption explicitly or check Linear/Notion. |
| "It's faster to rewrite this." | Big rewrites lose context and reviewability. Prefer the minimal pattern-matching change. |

## Rules

- Prefer pattern matching over invention.
- Prefer iteration speed over “big rewrite” speed.
- Never invent product behavior when the source of truth is missing; state the assumption.
- If the task becomes repetitive, propose capturing the workflow as a reusable skill.
