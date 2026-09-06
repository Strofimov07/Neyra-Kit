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
- If the change alters a signature or contract that other tests fake/mock (`fake_<fn>`,
  monkeypatched helpers, stub clients), grep the changed symbol across the test tree
  (`grep -rn '<symbol>' <tests-dir>`), run every file it returns, then the suite for the
  touched package — a targeted run stays green while a sibling mock drifts out of sync
  with the real signature, and CI catches it only after merge.
- **Confirm the gate you ran actually builds the changed target.** An app scheme that
  does not include a package reports `BUILD SUCCEEDED` while that package is broken; a
  root test command can skip a workspace member or sub-package. Build or test the changed
  unit through its own entry point (`swift test --package-path <pkg>`, the package's own
  `pytest` / `npm test`) and name that entry point in the report.
- **Take the exit code from the command itself, never from a pipe.** `xcodebuild … | grep
  -E "SUCCEEDED|error:" | tail` and `pre-commit … | tail -30` both exit 0 when the left
  side failed, and "no FAILED line in the output" is not a verdict — a build that could not
  find its destination printed neither. Run the command unpiped, or under `set -o pipefail`,
  or read `${PIPESTATUS[0]}`, and quote the code you read.

- A repo often has **several independent suites** (unit, integration, end-to-end,
  and a separate front-end runner) that no single command covers. Enumerate them
  once, prefer a single verify entry point that runs all of them, and when you run
  a subset, **name the suites you did not run** in the report. A suite nobody names
  is assumed green by everyone.

**Success criteria**
- Basic breakage is ruled out before runtime validation.

### 3. Run the real path

- For web UI, exercise the affected path in a real browser flow and name the path explicitly.
- For backend changes, hit the changed endpoint, job, or contract boundary.
- For multi-layer work, verify the seam where the change could actually break.
- For tests backed by real infrastructure (Redis, Postgres, a queue), run against the
  same backend CI uses or against an explicit fresh mock — and state which. Local
  fallbacks (in-memory limiter, in-memory store) hide what only the real backend shows:
  state surviving between tests, FK constraints.
- For a Node/JS surface, a green **local** `npm ci` is not proof: a `package-lock.json`
  built on the dev OS omits the Linux native-binding entries CI installs (rollup / esbuild
  / rolldown), and a newer local npm dedupes the tree differently than CI's. Reproduce CI's
  npm — `npx npm@<CI npm version> ci` (the CI npm version is a consumer fact; see
  `settings/`) — or confirm the lock carries the Linux binding, e.g.
  `grep -c '"node_modules/@rollup/rollup-linux-x64-gnu"' package-lock.json` ≥ 1.

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
| "I ran the tests." | Which ones? Repos carry several independent suites and a subset run reads as full coverage. Name the ones you skipped (step 2). |
| "It looks right in the diff." | Code review catches shape, not behavior. Run the real path. |
| "The unit tests pass, so it works." | A green unit test is not a green surface. Exercise the endpoint/flow. |
| "It's obviously correct." | "Obvious" changes are exactly the ones that ship broken. Verify anyway. |
| "There's no runtime/staging here." | Then verify the nearest observable proxy and name the blind spot — don't claim verified. |
| "I'll verify after merge." | After merge it's a production incident, not a check. Verify before closing. |
| "The targeted tests I ran are green." | Targeted scope proves the lines you touched, not the mocks and callers still assuming the old shape. Widen before pushing. |
| "It's green locally, CI will match." | Local fallbacks (in-memory store/limiter) are not the CI backend. Same backend or an explicit fresh mock — otherwise CI is your first real run. |
| "Local `npm ci` passed — the lock is fine." | A lock generated on macOS omits the Linux native-binding entries (rollup/esbuild) CI installs from, and a newer local npm dedupes differently. Reproduce CI's npm (`npx npm@<CI ver> ci`) or grep the `@rollup/rollup-linux-x64-gnu` entry before trusting green. |
| "The app scheme built green, so the package is fine." | A scheme builds only what it includes; a package it omits can be broken under a green build. Build the changed unit through its own entry point and name it (step 2). |
| "The output showed nothing alarming, so it passed." | You read a pipe's exit code, not the command's. Two verifications were declared done that way while the build and the pre-commit hook had both failed. Unpiped, `pipefail`, or `PIPESTATUS` — and quote the code (step 2). |

## Rules

- Do not treat mocked/component-only checks as sufficient for user-facing web UI final verification.
- A green local run of an infra-backed test is not proof: match CI's backend or use an
  explicit fresh mock, and say which.
- If the platform lacks a reliable success signal, verify the nearest observable proxy and name the blind spot.
- The exit code of the command is the verdict; a `| grep` / `| tail` over its output is not.
- Verify with the gate that builds the changed target, not with a scheme or root command that omits it.
