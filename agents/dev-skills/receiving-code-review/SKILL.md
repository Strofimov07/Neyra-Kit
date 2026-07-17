---
name: receiving-code-review
description: >-
  Disciplined consumption of code-review findings — read without reacting, verify
  each against the actual code, then implement by severity. No sycophancy, no
  reflexive agreement.
when_to_use: >-
  Use when responding to review findings (from `code-reviewer`, `spec-review`, a
  human reviewer, CI, or an automated PR reviewer like Cursor Bugbot — fetched by
  `pr-review-watch`) — before changing anything in response to feedback.
tools: Read, Grep, Glob
model: sonnet
---

# Receiving code review

## Goal

Action review findings correctly — fix what's real, push back on what's wrong with
evidence — instead of rubber-stamping every comment.

## Steps

1. **Read all findings without reacting** or editing anything yet.
2. **Restate** each finding in your own words.
3. **Verify** each against the actual codebase — is it true *here*?
4. **Evaluate**: real issue / false positive / matter of taste.
5. **Respond**: acknowledge real ones; push back on wrong ones with the evidence you found.
6. **Implement one at a time**, ordered: blocking/security → simple fixes → complex.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "The reviewer is right, just apply it." | A confidently-wrong finding implemented is a new bug. Verify against the code first. |
| "I'll fix everything in one big commit." | Batched unrelated fixes hide mistakes and break review. One finding at a time. |
| "Pushing back looks bad." | Wrong fixes look worse. Push back with evidence ("checked X — it does Y"). |

## Rules (anti-sycophancy)

- Never "You're absolutely right!" / "Great point!" before verifying against the code.
- If a finding is wrong, say so with the evidence you found — no apology theatre.
- Verify before implementing; order by severity (blocking/security first).
- One finding at a time; don't bundle unrelated changes.
