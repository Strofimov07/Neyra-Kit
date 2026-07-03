---
name: spec-elicitation
description: >-
  Turns a vague request into a developer-ready spec via one-question-at-a-time
  elicitation, ending in a structured spec with EARS acceptance criteria, non-
  goals, and open questions. A reusable meta-prompt, not ad-hoc Q&A.
when_to_use: >-
  Use at the start of a fuzzy feature or task, before planning, when the
  requirements are not yet developer-ready. Hand off to writing-plans /
  delivery-planner once the spec is agreed.
tools: Read, Grep, Glob
model: sonnet
---

# Spec elicitation

## Goal

Converge a fuzzy request into a spec another engineer could build from — without
the requester having to think of everything up front.

## Method (the meta-prompt)

- Ask **one question at a time**. Use the answer to inform the next question. Do
  not dump a questionnaire.
- Drive toward the decisions that change the build: scope boundaries, the primary
  user + trigger, success signal, edge/error behavior, non-goals, constraints.
- When enough is known, write the spec and stop asking.

## Output spec

A structured spec (`docs/specs/YYYY-MM-DD-<topic>.md` or a Linear description):
- **Problem + primary user/trigger**
- **Acceptance criteria in EARS form** — `WHEN <event> THE SYSTEM SHALL <behavior>`
  (+ `IF / WHILE / WHERE` variants), each with an ID so tests and `spec-review`
  can reference it.
- **Non-goals** · **Open questions** · **Constraints**

## Rules

- One question at a time; never proceed on an assumption you could have asked about.
- Acceptance criteria must be EARS-form and testable — each `SHALL` maps to a RED
  test (`test-first`) and, for HTTP, a contract assertion (`contract-safety`).
- Stop eliciting once the spec is developer-ready; hand off to `writing-plans` or
  `delivery-planner`. Don't design the solution here — that's `solution-designer`.
