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
