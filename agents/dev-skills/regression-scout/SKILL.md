---
name: regression-scout
description: >-
  Scans nearby behavior for likely regressions after a change: permissions,
  loading states, empty states, caching, polling, navigation, and adjacent flows.
when_to_use: >-
  Use near the end of implementation when the change touches shared UI,
  lifecycle code, state coordination, navigation, auth, or any area with high
  adjacent-breakage risk.
---

# Regression scout

## Goal

Find the most likely regressions before they find production.

## Scan list

### 1. Adjacent user states

- Check loading, empty, error, retry, offline, and permission-denied paths.

**Success criteria**
- The change is not only correct in the happy path.

### 2. Adjacent technical states

- Check caching, stale state, polling loops, subscriptions, and navigation return paths.

**Success criteria**
- Lifecycle or state edges are reviewed, not assumed safe.

### 3. Shared surface impact

- Ask what else uses the touched helper, component, endpoint, or store path.

**Success criteria**
- Shared dependencies with regression potential are identified.

### 4. Parser, extractor, and normalizer changes

- A change to a parser, extractor, regex, or normalizer is verified by **replaying
  it over populated real data**, not over fixtures. Fixtures encode the cases the
  author already imagined; the defects that survive review are fallback
  interception (a broader branch quietly capturing inputs an earlier branch used
  to own) and pathological input shapes (very long or unsegmented input turning a
  regex quadratic) — both pass unit tests.
- Compare before/after outputs over the same real sample and report the diff
  counts per field, including fields you did not intend to touch.

**Success criteria**
- A replay over real populated records was run, and per-field deltas are reported.

### 5. Report likely regressions

- Name the top few plausible regressions and whether they were checked or remain risks.

**Success criteria**
- Residual risk is concrete and reviewable.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "The parser change is covered by unit tests." | Fallback interception and pathological inputs pass fixtures and fail on real data. Replay it (step 4). |
| "Nothing else touches this." | Shared helpers/components/stores have non-obvious callers. Grep for them. |
| "The happy path works." | Loading/empty/error/permission-denied paths are where regressions live. Check them. |
| "It's just a UI tweak." | UI tweaks break navigation-return, caching, and state restoration. Scan the edges. |

## Non-goals

Deep correctness review of the change itself (`simplify-diff` / `code-reviewer`) and runtime verification (`verify-runtime`). This skill only scouts *adjacent* breakage, not the change's own correctness.

## Verification

The top plausible adjacent regressions are named, each marked as checked or as a residual risk.
