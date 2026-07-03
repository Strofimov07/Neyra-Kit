---
name: release-readiness
description: >-
  Performs a final production-readiness pass before closure: smoke path,
  rollback thinking, flags, monitoring, owner visibility, and residual risk.
when_to_use: >-
  Use before declaring a feature, fix, or backend behavior change done,
  especially when runtime behavior, user experience, or operational risk changed.
---

# Release readiness

## Goal

Decide whether the change is actually ready to ship or only ready to merge.

## Checklist

### 1. Verify the critical path

- Name and run the primary smoke path for the changed behavior.
- Prefer one real high-signal path over broad but shallow “looks fine” claims.

**Success criteria**
- The critical path was exercised and named explicitly.

### 2. Check rollout safety

- Note whether a feature flag, guard, or staged rollout exists.
- If none exists, state whether the risk is still acceptable.
- Consider rollback or containment path if the change fails in production.

**Success criteria**
- The team knows how risk would be contained after release.

### 3. Check operational visibility

- Ensure monitoring, analytics, and ownership are clear enough to detect regressions.
- Confirm the right follow-up note exists if visibility is partial.

**Success criteria**
- Post-release regressions would be observable by someone specific.

### 4. State residual risk honestly

- Separate:
  - verified
  - unverified
  - accepted risk
  - follow-up debt

**Success criteria**
- Release confidence is explicit and defensible.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's a small change." | Small changes cause outages precisely because no one smoke-tests them. Run the critical path. |
| "We'll monitor in prod." | You can't monitor what has no signal or owner. Confirm visibility before shipping. |
| "It worked in code review." | Review is not the runtime. Exercise the real path once. |
| "No rollback needed." | Then state explicitly why the risk is acceptable — don't leave it unstated. |
