---
name: writing-plans
description: >-
  Produces a granular, reviewable implementation plan as an artifact before any
  code — exact file paths, per-step code, expected output, and a forbidden-
  placeholder rule. The plan is the thing spec-review checks against.
when_to_use: >-
  Use before implementing a multi-step feature or change where a shared,
  reviewable plan reduces risk or enables delegation (subagent-dispatch). Skip
  for a one-file mechanical edit — say so.
tools: Read, Grep, Glob
model: sonnet
---

# Writing plans

## Goal

Turn approved intent into a plan an unfamiliar implementer could execute exactly
— so the plan can be reviewed *before* code exists, and so `spec-review` and
`subagent-dispatch` have a concrete artifact to work from.

## Audience frame

Write for a skilled engineer who knows **almost nothing about this codebase or
problem domain**. Every step must be self-contained: exact paths, real code, the
command to run, and the expected output. No "you know what I mean."

## Required sections (per task)

1. **Files** — Create / Modify / Test, each as a verbatim path from repo root.
2. **Interfaces** — signatures this task consumes from earlier tasks and produces
   for later ones.
3. **Steps** — ordered checkboxes, each with the actual code block (not
   pseudocode) and the command + expected output that proves it.
4. **Acceptance** — the EARS criteria (`WHEN … THE SYSTEM SHALL …`) the task satisfies.

## Forbidden placeholders (lint-enforced)

A plan MUST NOT contain: `TBD`, `TODO`, `FIXME`, `implement later`, `similar to`,
`add validation`, `write tests for the above`, `etc.` as a stand-in for real
content. These reopen the decisions the plan exists to close. Run `lint-plans.py`.

## Artifact

Save the plan as a committed artifact (`docs/plans/YYYY-MM-DD-<feature>.md`) or
attach it to the Linear issue. It is reviewable work product, not scratch.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "I know exactly what to build — a plan first is overhead." | The plan is the artifact `spec-review` checks the diff against (Goal); skip it and there's nothing to review against and delegation is impossible. Write it first — unless it's a one-file mechanical edit, in which case say so (when_to_use). |
| "I'll drop a TODO / 'similar to X' and fill it in while coding." | Those are lint-enforced forbidden placeholders — they reopen the exact decisions the plan exists to close. Resolve now or mark an open question to answer *before* coding, and run `lint-plans.py`. |
| "Pseudocode conveys the intent — real code blocks are excessive." | Steps require the actual code block plus the command and expected output that proves it (Required sections). Pseudocode leaves the hard decisions for the implementer to improvise. |
| "It's just scratch — I'll keep it in the chat." | The plan is reviewable work product, not scratch. Save it as a committed artifact (`docs/plans/…`) or attach it to the Linear issue (Artifact). |
| "I can't name the exact files yet, but I'll start planning anyway." | "A plan that can't name exact files isn't ready — inspect first" (Rules, `implementation-loop` step 1). Inspect the codebase, then write verbatim paths. |

## Rules

- No step ships with a placeholder; resolve the decision now or mark it an open
  question to answer before coding (not during).
- A plan that can't name exact files isn't ready — inspect first (`implementation-loop` step 1).
- Hand off to `subagent-dispatch` for delegated execution, or implement directly
  for small plans; either way `spec-review` checks the result against this plan.
