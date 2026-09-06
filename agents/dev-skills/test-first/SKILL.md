---
name: test-first
description: >-
  Writes a failing test that encodes the intended behavior before changing
  implementation, then makes it pass with minimal code and refactors under
  green (RED → GREEN → REFACTOR). Use when implementing or fixing logic a test
  can pin.
when_to_use: >-
  Use when implementing or fixing logic that a test can pin — bug fixes
  (reproduce first), new business rules, parsers/serializers, pricing & finance
  math, contract behavior, state machines, permission checks. Skip only when no
  meaningful automated check is possible (pure visual/layout) — and say so.
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Test first

## Goal

Encode the expected behavior as an automated check *before* touching
implementation, so the change is driven by a verifiable target instead of an
assumption — and so every fix ships with a regression guard that proves both
that the bug existed and that it is gone.

## Loop

### 1. RED — write the failing test first

- For a bug: write a test that reproduces it. For a new rule: write a test that
  asserts the rule. Reuse the repo's existing test harness, fixtures, and naming.
- Run it. Confirm it **fails for the intended reason** — the assertion you wrote,
  not an import error, typo, or missing fixture. A test that fails for the wrong
  reason is not RED.

**Success criteria**
- A failing test exists, named after the behavior, failing on the real assertion.

### 2. GREEN — minimal code to pass

- Write the smallest implementation that makes the test pass. No extra scope,
  no speculative options "while I'm here" (that's `implementation-loop`/YAGNI).
- Run the target test (green) and the surrounding suite (no new failures).

**Success criteria**
- Target test passes; no regressions introduced in the nearby suite.

### 3. REFACTOR — clean up under green

- With the test green, simplify (hand to `simplify-diff` / `code-reviewer`).
  Tests stay green throughout; behavior is unchanged.

**Success criteria**
- Code is cleaned; the suite is still green.

### 4. Hand off to verify-runtime

- `test-first` pins the unit/logic; `verify-runtime` proves the real surface
  (endpoint, browser flow, simulator). For user-facing or cross-layer work, run
  both — a green unit test is not a green real surface.

**Success criteria**
- The reviewer knows what the test proves and what still needs runtime verification.

## Static guards and ratchets

A guard test that parses source — a token-drift counter, an a11y label check, an
allowlist ratchet — is still a test: it must fail for the defect and only for the defect.

- **A metric that can be lowered by changing the spelling of the literal is not a
  metric.** Before a ratchet lands, name one transformation that lowers the counter
  without removing the defect (`style={{ backgroundColor: 'rgba(0,0,0,0.04)' }}` →
  `bg-black/[0.04]` dropped a hex / inline-style count and kept the literal). If one
  exists, the metric is incomplete — count the defect, not its notation.
- **An allowlist ratchet carries an obligation to shrink** — a dated target, or an
  assertion that the list never grows and decreases per release. Without it the
  allowlist hides the debt behind a green CI (measured: 46 % of the surface
  allowlisted, CI green, "no drift").
- **A static guard parses structure, never a fixed window.** "The label appears within
  the first 700 characters of the component body" went red on a comment; "the child
  within N lines of the parent" blamed the wrong element for the parent's background.
  Take the boundary by bracket/tag balance or the AST, so formatting and comments can
  neither move the defect out of frame nor an innocent line into it.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's a tiny change, I'll just write the code." | Tiny changes regress silently; the test is the guard. Write the test. |
| "I'll add the test after it works." | After-the-fact tests rubber-stamp whatever you wrote — including the bug. RED first proves the test *can* fail. |
| "I already see the fix." | Then the test costs ~60s and locks the fix in forever. Still write it first. |
| "There's no test harness here." | Check first (`grep` for the test runner/config). If there truly is none, say so and fall back to `verify-runtime` with a named proxy — don't silently skip. |
| "The bug is hard to reproduce in a test." | A repro you can't automate is one you can't prove fixed. Invest in the repro; if genuinely impossible, name the blind spot explicitly. |
| "The counter went down, so the drift is shrinking." | Only if no notation change can lower it. Name one that does; if it exists, the ratchet measures spelling, not defects (Static guards). |
| "A character window is good enough for a source guard." | A comment or a reformat moves the code out of the window and the guard goes red on an unrelated edit. Parse by bracket/tag balance (Static guards). |

## Rules

- A test written after the implementation is not test-first. The RED step is
  non-negotiable for bug fixes.
- The failing test must fail for the intended reason — verify the failure
  message before writing any implementation.
- Do not weaken, skip, or delete the test to make it pass; fix the code.
- `test-first` does not replace `verify-runtime` for user-facing or cross-layer
  surfaces — run both.
- If no automated check is feasible, state that explicitly and route to
  `verify-runtime`; never imply test coverage that does not exist.
- A source guard or ratchet counts the defect, not its notation; parses structure, not a
  window; and an allowlist ratchet must shrink on a schedule.
