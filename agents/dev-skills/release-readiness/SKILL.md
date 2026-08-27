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
- For payment, reward, or entitlement flows the smoke path must include **the grant**,
  not just the status transition. A paid order with no fulfillment branch looks identical
  to a successful purchase on every status signal — order marked paid, revenue counted,
  purchase event emitted — while granting the user nothing.

**Success criteria**
- The critical path was exercised and named explicitly.

### 2. Verify generated release artifacts

- If the release ships generated artifacts, validate the exact files and paths
  consumed by the publish or deploy step, not only the command that produced them.
- Run the surface-specific artifact validator when one exists; keep product- and
  platform-specific constraints in that validator rather than this root skill.
- If the shipped artifact was not checked, classify that path as unverified.

**Success criteria**
- The artifact that will actually ship was validated, or the release remains
  explicitly not production-ready for that path.

### 3. Check whether the release changed what the product is

- A release that adds the first payment, the first personal-data store, the first
  metered-API call, the first long-running job, or the first real users changes
  which disciplines are mandatory from now on. Update `settings/product.yml` in
  the same change; the gates follow the declaration, not the intention.

**Success criteria**
- Either no capability flag changed, or the profile was updated with the release.

### 4. Check rollout safety

- Note whether a feature flag, guard, or staged rollout exists.
- If none exists, state whether the risk is still acceptable.
- Consider rollback or containment path if the change fails in production.

**Success criteria**
- The team knows how risk would be contained after release.

### 5. Check operational visibility

- Ensure monitoring, analytics, and ownership are clear enough to detect regressions.
- Confirm the right follow-up note exists if visibility is partial.

**Success criteria**
- Post-release regressions would be observable by someone specific.

### 6. State residual risk honestly

- Separate:
  - verified
  - unverified
  - accepted risk
  - follow-up debt
**Success criteria**
- Release confidence is explicit and defensible.

### 7. Close the follow-up loop

- Every follow-up gets a ticket **before** closure: a `Follow-up:` line in a commit or
  PR body, and any unresolved item in the issue's own acceptance / "remaining to close"
  list, becomes its own tracker issue. A follow-up living only in a merged commit message
  is not tracked debt, it is lost debt — nobody re-reads merged commit bodies.
- The only alternative is an explicit "no ticket needed" decision recorded on the issue
  **and naming who accepted the debt**. An agent-authored "not needed" with no named
  owner does not count.
- Never move an issue to done while it still carries open, unticketed acceptance items.
- Before closing, re-read the issue's **full body** and enumerate its acceptance criteria,
  then confirm each is met. Working from the title or a summary is how an AC you never read
  becomes an AC you never met — verify the list, not your memory of it.

**Success criteria**
- Every named follow-up exists as a ticket, or as a recorded no-ticket decision with an
  owner — not only as prose in a commit, PR, or chat.
- Every acceptance criterion in the issue body is confirmed met before the issue is closed.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "It's a small change." | Small changes cause outages precisely because no one smoke-tests them. Run the critical path. |
| "We'll monitor in prod." | You can't monitor what has no signal or owner. Confirm visibility before shipping. |
| "It worked in code review." | Review is not the runtime. Exercise the real path once. |
| "The generator/test passed." | Producer success does not prove the published artifact is the expected file or content. Validate the exact artifact consumed by publish/deploy. |
| "No rollback needed." | Then state explicitly why the risk is acceptable — don't leave it unstated. |
| "I noted the follow-up in the commit/PR body." | Merged commit bodies are write-only; nobody re-reads them. File the ticket now, or record an explicit no-ticket decision on the issue. |
| "The remaining items are small, closing anyway." | The issue's own acceptance list is the closure contract. Ticket what's left, or leave it open. |
| "The diff does what the title says — close it." | The title is a label, not the DoD. Read the full issue body, enumerate its acceptance criteria, and confirm each — an AC you never read is one you never met. |
