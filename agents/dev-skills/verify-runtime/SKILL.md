---
name: verify-runtime
description: >-
  Verifies code changes on the strongest practical runtime path for the affected
  surface, including real browser flows for web UI work and explicit reporting
  of unverified gaps.
when_to_use: >-
  Use before closing implementation work, especially for user-facing UI,
  cross-layer changes, contract changes, or anything that could appear correct
  in code review but fail on the real surface.
---

# Verify runtime

## Goal

Prove that the shipped change works on the real surface, not only in static analysis.

## Verification order

### 1. Choose the strongest practical checks

- Prefer the highest-signal validation available for the touched surface:
  - unit/integration tests for business logic and contracts
  - Playwright or equivalent real-browser path for web UI
  - simulator/runtime path for iOS when the task affects actual behavior
  - targeted smoke path for backend or integration changes

**Success criteria**
- A concrete verification plan exists before commands are run.

### 2. Run narrow checks first

- Start with targeted tests or build/lint checks that should fail fast.
- Fix deterministic failures before broadening verification.

**Success criteria**
- Basic breakage is ruled out before runtime validation.

### 3. Run the real path

- For web UI, exercise the affected path in a real browser flow and name the path explicitly.
- For backend changes, hit the changed endpoint, job, or contract boundary.
- For multi-layer work, verify the seam where the change could actually break.

**Success criteria**
- The changed behavior is observed on a real surface or contract boundary.

### 4. Record confidence honestly

- Distinguish:
  - checks completed
  - checks skipped
  - checks blocked
  - residual risk
- If verification is partial, keep the task summary honest and do not imply full completion.

**Success criteria**
- Reviewers know exactly what confidence level the change has.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It looks right in the diff." | Code review catches shape, not behavior. Run the real path. |
| "The unit tests pass, so it works." | A green unit test is not a green surface. Exercise the endpoint/flow. |
| "It's obviously correct." | "Obvious" changes are exactly the ones that ship broken. Verify anyway. |
| "There's no runtime/staging here." | Then verify the nearest observable proxy and name the blind spot — don't claim verified. |
| "I'll verify after merge." | After merge it's a production incident, not a check. Verify before closing. |

## Rules

- Do not treat mocked/component-only checks as sufficient for user-facing web UI final verification.
- If the platform lacks a reliable success signal, verify the nearest observable proxy and name the blind spot.
