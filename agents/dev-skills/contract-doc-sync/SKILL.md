---
name: contract-doc-sync
description: >-
  Ensures contract-layer documentation stays in sync with backend and platform
  changes: endpoint registry, scheduled jobs, technical specs, and runbooks.
when_to_use: >-
  Use when backend or platform work changes endpoint behavior, auth, side
  effects, schedules, failure handling, or any documented contract surface.
---

# Contract doc sync

## Goal

Prevent backend/platform changes from shipping without matching contract documentation.

## Checklist

### 1. Identify documentation targets

- Determine which registries, specs, runbooks, or architecture pages own the changed contract.

**Success criteria**
- Canonical doc owners are explicit.

### 2. Check delta

- Compare the code change to current docs and note what is now stale.

**Success criteria**
- Documentation drift is concrete, not vague.

### 3. Sync in the same cycle

- Update the registry or spec in the same execution cycle when possible.
- If blocked, record explicit documentation debt with owner/follow-up.

**Success criteria**
- Contract docs either match the code or the debt is explicitly tracked.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "The code change is what matters — I'll update the registry/spec later." | "Later" ships the drift: a stale contract registry listed namespaces whose apps were deleted and sent agents hunting for code that no longer existed. Sync in the same execution cycle (step 3). |
| "It's an internal endpoint — nobody reads its docs." | The registry/spec is a canonical input other gates trust (contract-checker); a wrong entry makes a correct gate wrong. Identify the doc owner (step 1) and update it. |
| "I can't update the doc right now, so I'll skip it." | A silent skip isn't an option. If blocked, record explicit documentation debt with owner and follow-up (step 3) so the drift is tracked, not lost. |
| "It's a small change — the docs are close enough." | "Documentation drift is concrete, not vague" (step 2). Compare the code change to current docs and name exactly what is now stale. |
