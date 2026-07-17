---
name: pr-review-watch
description: >-
  After a PR is opened or pushed, watches for the automated PR reviewers the
  repo has wired (Cursor Bugbot, CI review annotations) — which post findings
  asynchronously — and surfaces them by severity, then hands off to
  receiving-code-review. Read-only: never auto-applies a fix, dismisses a
  finding, or merges past an unreviewed one.
when_to_use: >-
  Use right after pr-hygiene opens or pushes to a PR, whenever the repo has an
  automated PR reviewer (e.g. Cursor Bugbot). Also when asked "what did Bugbot
  find on PR #N". The pre-merge twin of post-merge-watch.
---

# PR review watch

## Goal

Close the "opened the PR, Bugbot found a High-severity bug, nobody read it
before merge" window. Automated PR reviewers post **asynchronously** — a Bugbot
pass typically lands a couple of minutes after the push — and their findings
hide behind API quirks, so without an active watch they get merged past
silently. This skill is the active half between `pr-hygiene` (opens the PR) and
`receiving-code-review` (acts on the findings).

## Protocol

### 1. Establish which automated reviewers are wired

- Cursor Bugbot present? Check for a review authored by `cursor` on a recent PR,
  or the repo's Bugbot config. CI checks that annotate the diff also count.

**Success criteria**
- The set of automated reviewers is named; "no automated reviewer wired" is a
  valid, stated outcome (like post-merge-watch's "no CI wired").

### 2. Watch for the review to land — bounded window

- The review is async: an open PR with **no** Bugbot summary yet means *not
  reviewed yet*, NOT *clean*. Poll until the summary review appears or the
  window expires (default 5 min; state it).
- Each new push re-triggers a fresh pass — watch after the push that matters,
  not a stale earlier one.

  ```bash
  # Did Bugbot run, and how many issues? (summary review — author login `cursor`)
  gh pr view <PR> --json reviews \
    --jq '.reviews[] | select(.author.login=="cursor") | .body' \
    | grep -oE 'found [0-9]+ potential'
  ```

**Success criteria**
- Reported as one of: "Bugbot: N issues", "Bugbot: 0 issues (clean)", or
  "not posted yet — window expired: <PR link>". Never silent, never a guess.

### 3. Fetch the actual findings — mind the two logins

- The summary review is authored by `cursor`; the **inline findings are a
  different login, `cursor[bot]`**. Selecting the wrong one returns empty and
  you will wrongly conclude "no findings." Each finding carries a severity
  (`High`/`Medium`/`Low`) and a `BUGBOT_BUG_ID`.

  ```bash
  # Inline findings — note the [bot] suffix on the REST user.login
  gh api "repos/{owner}/{repo}/pulls/<PR>/comments?per_page=100" \
    --jq '.[] | select(.user.login=="cursor[bot]")
          | ([.body | scan("High Severity|Medium Severity|Low Severity")][0] // "?") as $severity
          | "• [\($severity)] \(.path):\(.line // .original_line)\n\(.body)"'
  ```

**Success criteria**
- Every finding the summary count promised is retrieved; a count/retrieved
  mismatch is investigated, not ignored.

### 4. Surface by severity, then hand off

- List findings High → Medium → Low in the same turn, each with `path:line`.
- Hand off to `receiving-code-review` — automated reviewers produce false
  positives; verify each against the code before acting. Do not auto-apply
  "Fix in Cursor" and do not dismiss a finding without a verified reason.

**Success criteria**
- Findings are visible in the conversation before merge; each High finding has
  (or is queued for) a receiving-code-review verdict, not a hand-wave.

## Common rationalizations (and why they're invalid)

| The excuse | Why it's wrong → what to do |
|---|---|
| "PR's open, no comments — clean, merge it." | Bugbot is async; empty may mean *not reviewed yet*. Confirm the summary review exists (step 2) before calling it clean. |
| "Queried the comments, got nothing." | You likely selected `cursor`, not `cursor[bot]` — inline findings use the bot login. Re-query (step 3). |
| "It's probably a false positive, merge past it." | Probably ≠ verified. A real High merged is a prod bug. Run it through receiving-code-review first. |

## Rules

- Read-only on the PR — never auto-apply a fix, dismiss a finding, or merge.
- Bounded, stated window; "not reviewed yet" is never reported as "clean".
- Two logins: summary = `cursor`, inline findings = `cursor[bot]`.
- Every High-severity finding gets a receiving-code-review verdict before merge.

## Non-goals

Acting on the findings (`receiving-code-review` → `implementation-loop`),
post-merge CI/deploy (`post-merge-watch`), and the PR's own required status
checks (that's the PR's gate, not an advisory review).

## Verification

The session transcript shows, for the open PR, the Bugbot summary count and each
finding surfaced by severity — or an explicit "not wired" / "window expired, not
yet posted: <link>" — before the merge.
