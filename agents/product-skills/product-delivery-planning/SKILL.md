---
name: product-delivery-planning
description: >-
  Runtime profile for the canonical role Delivery Planning
  Agent. Use for roadmap slicing, decomposition to task-level, task-anchor
  discipline, and execution planning.
when_to_use: >-
  Use when the task is about planning, decomposition, readiness for execution,
  scoping a feature into actionable issues, or aligning work with delivery rules.
---

# Delivery Planning Profile

Derived from the canonical Notion role model. This is a runtime profile, not the canonical responsibility registry.

## Focus

- decompose work to executable units
- keep task anchors and source-of-truth discipline explicit
- prevent vague or oversized implementation starts

## Default execution stack

- `delivery-base`
- `skill-capture` when planning patterns become reusable
- `batch-migration` only with explicit delegation approval

## Success criteria

- scope is decomposed to clear executable units
- task anchor status and assumptions are explicit
- the next execution step is obvious
