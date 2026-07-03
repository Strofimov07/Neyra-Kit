---
name: post-merge-watch
description: >-
  After a human-approved merge lands, watches the resulting CI/CD pipeline
  (build, tests, deploy) and proactively surfaces failures instead of leaving
  the human to notice later. Read-only — never retriggers, cancels, or
  modifies a pipeline.
when_to_use: >-
  Use as the final step after pr-hygiene's merge, whenever the target repo has
  CI/CD wired to the merge branch. Also when the user asks "did the deploy go
  through" after a recent merge.
---

# Post-merge watch

## Goal

Close the "merged green, deploy silently red" window: the approval gate ends
at the merge, but the pipeline it triggers can still fail — someone must be
watching, and it shouldn't have to be a human's memory.

## Protocol

### 1. Identify what the merge triggers

- From the repo's CI config (`.github/workflows/`, known project pipelines —
  e.g. per-project facts in `settings/facts/`): which workflows fire on the
  merge target, and which of them deploy.

**Success criteria**
- The watched pipeline set is named; "no CI wired" is a valid, stated outcome.

### 2. Watch for a bounded window

- Poll status (`gh run list --branch <target> --commit <sha>` or the repo's
  equivalent) until terminal state or the window expires (default: 10 min for
  build/test, longer only if a deploy stage is known-slow — state the window).
- Read-only. Never retrigger, cancel, or approve anything.

**Success criteria**
- Every watched run reaches a reported terminal state or an explicit
  "window expired, still running: <link>".

### 3. Surface the result in the same turn

- Red: report immediately — failing job, link, and the merge commit that
  triggered it. Do not move on to the next task silently.
- A pipeline that is **already known-broken** (per `settings/facts/`): state
  that it is pre-existing rather than re-alarming — but still surface it once
  per session so it isn't forgotten.

**Success criteria**
- A failure is visible in the conversation before any new work starts;
  known-broken is distinguished from newly-broken.

### 4. Capture

- A newly-broken pipeline after your merge → that's your regression until
  proven otherwise: hand off to `systematic-debugging` / `incident-runbook`,
  don't just report and walk away.

**Success criteria**
- Newly-red pipelines get an owner action (fix / revert proposal / filed
  issue), not just a mention.

## Deterministic backstop (not this skill, but part of the contract)

The Stop-gate hook independently checks the default branch's latest CI
conclusion at session end (`hooks/stop-gate.sh`) and blocks once per session
if it turned red — so a forgotten watch still gets caught at the session
boundary. This skill is the active half; the hook is the net.

## Rules

- Read-only on pipelines, always.
- Bounded window, always stated — "I'll keep an eye on it" without a window
  is not a watch.
- Newly-red after your merge = yours by default; known-broken = say so once.

## Non-goals

Fixing the pipeline (systematic-debugging / incident-runbook), re-running
flaky jobs, and pre-merge CI checks (that's the PR's own checks).

## Verification

The session transcript shows the terminal state (or expired-window link) for
every pipeline the merge triggered, before subsequent work.
