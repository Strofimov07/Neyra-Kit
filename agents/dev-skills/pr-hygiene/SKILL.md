---
name: pr-hygiene
description: >-
  Branch, commit, and PR mechanics: branch off the default
  branch, stage explicit paths, clean messages with no AI attribution, and a PR
  body in the required format. Use when committing, branching, or opening a PR.
when_to_use: >-
  Use when about to commit, create a branch, or open a pull request — especially
  on a default branch, with a dirty/entangled tree, or across multiple repos.
---

# PR hygiene

## Goal

Land changes as small, reviewable, correctly-attributed commits/PRs without sweeping unrelated work.

## Branch & merge policy

- **Everything goes through a PR.** Never push commits straight to the merge target; branch → commit → PR → merge.
- **Pick the integration target up front: `dev` if it exists, else `main`.** Check with `git branch -a` / `git show-ref --verify refs/remotes/origin/dev`; branch off that target and point the PR at it.
- **One change = one branch = one PR**, named `feat/…` / `fix/…` / `chore/…`.
- **Clean up after merge:** delete the remote branch (or rely on GitHub auto-delete) and the local branch (`git branch -d`), then `git fetch --prune`. Don't let merged branches accumulate.
- **Never strand WIP across a branch switch:** know your base; commit or stash before `git checkout`; after switching, confirm `git branch --show-current` and the base. (This is the time-sink when a tree gets reset under you.)

## Steps

1. **Branch first** — never commit straight to the merge target (`dev` if it exists, else `main`); branch off it.
2. **Scope the stage** — `git add` explicit paths for THIS change. Never `git add -A` when the tree has unrelated or pre-existing changes. Review `git diff --cached --stat` before committing.
3. **Commit message** — imperative subject + a body that explains what and why. No `Co-Authored-By: Claude`, no "Generated with Claude Code" or any AI attribution — write as the author.
4. **PR body** — follow the repo's PR Delivery Format (summary, changes, verification, risks); no AI attribution footer.
5. **Title honesty (NEB-1407)** — before opening the PR, compare the title's claimed scope against `git diff --stat` top-level paths. The title must not claim a surface the diff doesn't touch (a "monetization + iOS build repair" title over a diff with zero `ios/` files misleads changelogs, release notes, and delivery-audit). Mismatch → fix the title, not the expectation.
6. **Don't mix concerns** — split unrelated changes into separate commits/PRs.
7. **Clean baseline before starting** — for a new branch/worktree, verify the test baseline is green *before* layering work, so a later failure is attributable to your change, not inherited.
8. **Destructive ops need explicit confirmation** — `git reset --hard`, `git clean -fd`, `branch -D`, `worktree remove`, or discarding a branch require an explicit, typed user confirmation naming what will be lost. Never discard work to "clean up".

## Success criteria

- index contains only the intended files (verified via `git diff --cached --stat`)
- work is on a feature branch off the right target (`dev` if it exists, else `main`), not the target itself
- message + PR body carry no AI attribution and match the repo format
- after merge, the branch is deleted and `git fetch --prune` run (no stale branches)

## Non-goals

Code review (`simplify-diff` / `code-reviewer`) and release readiness (`release-readiness`) — separate skills.

## Verification

`git diff --cached --stat` shows only the intended paths; `git branch --show-current` is not the default branch.
