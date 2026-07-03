---
name: batch-migration
description: >-
  Plans and executes large mechanical changes as independent units with explicit
  verification paths. Use only when the user explicitly asks for delegation,
  parallel work, or a sweeping multi-file migration.
when_to_use: >-
  Use when the user explicitly wants batch execution, parallel agents, or a
  broad migration that can be decomposed into independent slices. Do not use
  for tightly coupled or small changes.
---

# Batch migration

## Goal

Turn a sweeping change into independently verifiable work units without losing consistency.

## Workflow

### 1. Research and decompose

- Map the affected modules, patterns, and call sites.
- Split work by stable boundaries: module, directory, feature slice, or contract family.
- Avoid units that depend on sibling units landing first.

**Success criteria**
- Each work unit is independently implementable and reviewable.

### 2. Define the verification recipe up front

- Decide how each unit proves success end-to-end.
- If no concrete verification path exists, stop and ask for one instead of guessing.

**Success criteria**
- Every unit has a realistic validation path.

### 3. Execute only with explicit user approval for delegation

- Parallel or delegated execution is allowed only when the user explicitly asks for sub-agents or parallel work.
- If that approval is absent, keep the plan local and sequential.

**Success criteria**
- Delegation policy is respected.

### 4. Reconcile outputs consistently

- Ensure each unit follows the same conventions, contracts, and naming.
- Track completion, failures, and follow-up work per unit.

**Success criteria**
- The batch change reads like one coherent migration, not unrelated patches.
