---
name: localization-guard
description: >-
  Protects the localization contract for user-facing changes: no hardcoded UI
  strings, required locales covered, and runtime language switching respected.
when_to_use: >-
  Use when adding or changing user-facing copy, prompts, CTAs, settings text,
  onboarding steps, upsells, empty states, or errors on localized surfaces.
---

# Localization guard

## Goal

Prevent user-facing changes from bypassing the app's localization system.

## Checklist

### 1. Find all new or changed strings

- Enumerate every user-visible string introduced or modified in the task.

**Success criteria**
- No new user-facing string is left unreviewed.

### 2. Check localization path

- Confirm strings go through the existing localization contract for the surface.
- Reject hardcoded UI strings in runtime code paths.

**Success criteria**
- All affected strings use the proper localization mechanism.

### 3. Check locale coverage

- Verify minimum required locales for the surface.
- For Browser, at least `en` and `ru` must remain aligned.

**Success criteria**
- Required locales are updated consistently.

### 4. Check runtime behavior

- If the app supports runtime language switching, ensure the changed strings participate correctly.

**Success criteria**
- The localized behavior matches existing app expectations.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "I'll localize it later." | Hardcoded strings ship and never get back-filled. Route through the localization path now. |
| "It's just a debug/error string." | Users see error and empty states; they need locales too. Localize unless it's truly dev-only. |
| "Only en for now, ru later." | Divergent locales are a silent contract break. Keep en + ru aligned in the same change. |
