---
name: trust-boundary-review
description: >-
  Reviews AI and product changes for permission boundaries, user confirmation,
  destructive actions, hidden side effects, data exposure, and auditability.
when_to_use: >-
  Use when a feature can act on behalf of the user, access sensitive data,
  trigger external side effects, or make high-trust decisions without obvious UI friction.
---

# Trust boundary review

## Goal

Ensure high-trust features behave safely and transparently.

## Checklist

### 1. Identify authority and side effects

- Name what the feature can read, write, send, delete, or trigger.

**Success criteria**
- The trust boundary is explicit.

### 2. Check confirmation and visibility

- Verify whether the user sees what will happen before irreversible or sensitive actions.

**Success criteria**
- Destructive or sensitive actions have the right checkpoint.

### 3. Check hidden consequences

- Look for silent network actions, background side effects, unexpected persistence, or data sharing.
- When tests initialize an application runtime, verify production-facing clients
  are disabled, replaced, or explicitly allowlisted. Unexpected external egress
  is a failure even when the functional test passes.

**Success criteria**
- Side effects are transparent enough for the surface's trust model, and test
  runtimes do not contact unintended external services.

### 4. Check auditability

- Confirm whether failures and important actions would leave enough evidence for debugging or support.

**Success criteria**
- Operators or support can reconstruct what happened when needed.

### 5. Individual-performance judgments — destructive tier

- If the feature or flow surfaces a judgment about a specific person's
  performance, employment, or standing (ratings, low-performer flags,
  improvement plans), treat it as destructive-tier regardless of how it's
  framed: output is a **candidate with an evidence trail, never a verdict**;
  a human decision gate is mandatory before anything moves; drafts only —
  nothing about a person is sent, filed, or written to an external system
  (HRIS, email, tracker) by the agent; the data lives in a private,
  non-published store (`settings/private/`), physically separate from
  team-level reporting.

**Success criteria**
- Person-level judgments cannot reach any surface without an explicit human
  verdict, and their data path never crosses into shared reports or
  published artifacts.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "Tests are harmless." | Hosted and integration tests can boot real application clients. Prove external clients are isolated or explicitly allowlisted. |
| "The test passed." | Functional success says nothing about hidden egress. Inspect runtime evidence and fail on unexpected external endpoints. |
