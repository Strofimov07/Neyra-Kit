---
name: parallel-lanes
description: >-
  Gives each simultaneously-running agent its own isolated lane — one git
  worktree (or at least one branch + explicit-path commits), one Linear ticket,
  one branch — so concurrent agents cannot collide on the git index, the branch
  pointer, or working-tree files. Includes an integration step to merge
  completed lanes and a kit VERSION bump when the change is to the kit itself.
when_to_use: >-
  Use whenever two or more agents will work in the same repository at the same
  time. Do NOT skip because the parallel work "feels small" or "only touches
  different files" — index and branch-pointer collisions happen regardless of
  file overlap. Pairs with subagent-dispatch (sequential ledger) and
  writing-plans (per-lane plan + declared interfaces).
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Parallel lanes

## Goal

Let two or more agents work in one repository at the same time without touching
each other's branch, index, or working-tree files — then integrate the completed
lanes cleanly.

## Protocol

### 1. Assign one lane per agent before any work starts

Each parallel agent gets, up front:

- **One Linear ticket** (`NEB-XXXX`) — never shared across lanes.
- **One branch** — `feature/<NEB-XXXX>-<slug>`, from an agreed base (record it:
  `git rev-parse HEAD`).
- **One git worktree** (strongly preferred) — `git worktree add
  ../wt-NEB-XXXX feature/NEB-XXXX-slug`. Each worktree has its own working tree
  and index, so the agents never share either.

If worktrees aren't possible, fall back to branch-per-lane in one tree — but then
the hard rules in step 2 are the *only* protection, not belt-and-suspenders.

**Success criteria**
- Every parallel agent has exactly one ticket, one branch, and one worktree (or
  an explicit record that the hard rules are the sole protection).
- The BASE commit is recorded per lane before dispatch.

### 2. Hard rules for every agent in a parallel run

Not guidelines. Violating any one can silently corrupt a sibling's work.

- **Never `git add -A` / `git add .` in a shared tree.** Stage explicit paths
  only: `git add src/foo.py tests/test_foo.py`.
- **Never `git checkout <branch>` / `git switch` in a tree a sibling is using** —
  it moves HEAD and rewrites the working tree.
- **Never `git stash` / `git reset --hard` / `git clean` in a shared tree** —
  each can destroy the other lane's uncommitted work.
- **Commit to your own branch only.** No push/merge to `dev`/`main` during the
  run; that is the integration step.
- **Files in the tree that aren't yours: leave them.** Don't move, delete, or
  stage them. If they block you, report BLOCKED to the orchestrator.

**Success criteria**
- No agent touched a file, branch, stash, or index entry outside its own lane.

### 3. Work within your lane

- Run `implementation-loop` + the gate skills as normal, inside the lane.
- Every commit stages explicit paths and names the lane's branch/ticket.
- Any cross-lane interface (a signature one lane produces and another consumes)
  is declared in the plan's **Interfaces** section before dispatch — see
  `writing-plans`.
- **Mid-flight independence re-check (NEB-1402):** the pre-dispatch
  independence assumption expires when your real analysis starts. The moment
  your spec/analysis work surfaces a file, table, or contract a sibling
  lane's scope claims — report `BLOCKED: dependency-conflict` immediately so
  the orchestrator pauses the batch for re-approval. Never absorb the
  overlap into your own lane.

**Success criteria**
- The lane's branch has a narrow, clean history touching only its own files.
- Implemented signatures match the up-front declared interfaces.
- Discovered cross-lane overlaps were reported as BLOCKED, not worked around.

### 4. Coordinate and integrate

When a lane is ready:

1. Review each lane's diff independently (`code-reviewer` + `spec-review`)
   before touching the integration branch.
2. Merge lanes one at a time via `pr-hygiene` (one branch = one PR; integration
   target `dev` if it exists, else `main`): `git merge --no-ff
   feature/NEB-XXXX-slug`. Resolve conflicts explicitly — never `-X theirs`.
3. After each lane lands, run `verify-runtime` + `regression-scout` on the
   **integrated** surface, not just the lane in isolation.
4. Delete the lane: `git branch -d feature/NEB-XXXX-slug && git worktree remove
   ../wt-NEB-XXXX`.

**Success criteria**
- Each lane reviewed and green before it touches the integration branch.
- No lane's files appear in another lane's diff.
- `verify-runtime` passes on the post-merge state.

### 5. Kit VERSION bump (only when the change is to the kit itself)

- Increment `VERSION` inside the single lane that carries the kit change — no
  other lane touches `VERSION`.
- Re-install into the consumer repo (`install.sh`) ONLY after every sibling
  lane's uncommitted WIP is committed — a re-install's `rsync --delete`
  overwrites the shared `agents/dev-skills/` tree and can delete a sibling's
  uncommitted skill files. See EVOLVING-THE-KIT.md.

**Success criteria**
- `VERSION` changed in exactly one commit, in the lane that owns the kit change.

## Common rationalizations — do not accept these

- "Files don't overlap, so `git add -A` is safe." The index is shared; any
  untracked file in the tree gets swept up.
- "Faster to just switch the branch here." A switch rewrites the tree and moves
  HEAD — the sibling's uncommitted work is stranded.
- "I'll stash the other agent's changes and restore them after." Stash refs are
  fragile; you will not reliably restore them.
- "Same user's agents, so it's fine." Same machine, same dirty tree — the
  collision mechanics are identical to a two-developer shared checkout.
- "The overlap I just discovered is small — I'll handle it in my lane." The
  independence assumption was the dispatch's approval basis; it expired the
  moment you found the overlap. Report BLOCKED and let the batch re-approve.

## Rules

- One ticket + one branch + one worktree per parallel agent. No exceptions.
- Never `git add -A` in a parallel run, even in a dedicated worktree.
- Never switch branches or run destructive git in a tree a sibling is using.
- Integration (merge + verify-runtime + regression-scout) is a named phase, not
  optional.
- Kit VERSION bumps in the one lane that owns the kit change; never in two.
