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

## Rules

- No step ships with a placeholder; resolve the decision now or mark it an open
  question to answer before coding (not during).
- A plan that can't name exact files isn't ready — inspect first (`implementation-loop` step 1).
- Hand off to `subagent-dispatch` for delegated execution, or implement directly
  for small plans; either way `spec-review` checks the result against this plan.
