---
name: analytics-instrumentation
description: >-
  Defines and verifies analytics coverage for a feature: event map, payload,
  owner, observable proxy, limitation, and runtime trigger coverage.
when_to_use: >-
  Use when a change affects user behavior, funnels, activation, onboarding,
  conversion, retention, fallback paths, or any product question that should be
  answered with instrumentation instead of guesses.
---

# Analytics instrumentation

## Goal

Make the feature measurable enough to support product decisions.

Boundary: this skill is event-coverage QA (does the feature emit the right events,
with the right payload, observably?). The strategic framing — which metrics/experiments
to run, funnel and retention design — is `growth-analytics`
(`growth-product-analytics`), not this skill.

## Workflow

### 1. Define the desired metric

- Name the product outcome the team actually wants to measure.
- If the platform cannot expose it directly, define the closest observable proxy.

**Success criteria**
- Desired metric and observable proxy are both explicit.

### 2. Define the event map

- Specify trigger, payload, destination, owner, and failure/fallback events.
- Check naming against existing event conventions.

**Success criteria**
- The changed flow has an explicit event map.

### 3. Verify trigger coverage in code

- Confirm the event fires at the actual runtime point and not only in an idealized path.
- Check that fallback/error/cancel paths are not invisible.

**Success criteria**
- Instrumentation exists on the real trigger points.

### 4. Document limitation

- Name the blind spot if the observed event is only a proxy.
- Do not imply business certainty that the platform cannot support.

**Success criteria**
- Product analytics claims remain honest.
