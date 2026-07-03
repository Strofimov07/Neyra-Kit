---
name: systematic-debugging
description: >-
  Roots out a novel bug by investigation before any fix — reproduce → root
  cause → pattern analysis → one written hypothesis → fix with a failing test.
  Stops guess-and-check.
when_to_use: >-
  Use for a NOVEL bug, a failing or flaky test, or a "why is X happening?" where
  the cause is not yet understood. Not for known production incidents (use
  `incident-runbook` — containment first) or greenfield logic (use `test-first`).
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Systematic debugging

## Governing rule

No fix without a root-cause investigation first. A fix applied before you can
name the cause is a guess — and the first guess sets the pattern for the next ten.

## Phases

### 1. Reproduce + root cause

- Reproduce the failure reliably. A bug you can't reproduce is one you can't
  prove fixed.
- Read the actual error and stack trace — every line, not a skim.
- Locate where the bad state *originates*, not where it surfaces.

**Success criteria**
- A reliable reproduction exists and the origin (not the symptom) is identified.

### 2. Pattern analysis

- Find a working example of the same pattern in the repo; diff the broken path
  against it. Read every line — the difference is usually small and easy to skim past.

**Success criteria**
- The broken path is compared against a known-good one; the divergence is named.

### 3. Hypothesis — one variable

- Write ONE hypothesis: "X happens because Y." Change ONE variable to test it.
- If it's wrong, discard it and form the next — never stack speculative changes.

**Success criteria**
- A single written hypothesis was tested by changing a single variable.

### 4. Fix with a failing test

- Encode the reproduction as a failing test (hand to `test-first`), then fix.
- Confirm the test goes green and the surrounding suite stays green.

**Success criteria**
- The fix is locked in by a regression test; no new failures.

## Stop condition

If three or more fixes have failed, **stop** — this is not a failed hypothesis,
it's the wrong architecture or mental model. Step back and re-frame, or escalate.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's an emergency — just try a fix." | For a *known* incident use `incident-runbook`. For a novel bug, guess-and-check is slower because the first wrong fix hides the cause. Investigate. |
| "I'll investigate after it works." | Once it "works" you'll never find the real cause and it resurfaces. Find the cause now. |
| "One quick fix first." | The first fix sets the pattern and masks the root cause. Form a hypothesis first. |
| "I see the symptom, I'll patch there." | Patching the surface leaves the source; it reappears elsewhere. Trace to the origin. |

## Rules

- Reproduce before you theorize.
- One hypothesis, one variable — never stack speculative changes.
- 3+ failed fixes = wrong model: stop and re-frame, don't keep patching.
- Pairs with `test-first`: phase 4 is a failing reproduction test.
- For known production incidents, use `incident-runbook` (containment first), not this skill.
