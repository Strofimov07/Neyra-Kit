---
name: goal-mode
description: >-
  Opt-in autonomous orchestration: given a goal, the kit drives the loop
  (decompose → dispatch → gate → integrate → re-evaluate) with hard caps and
  mandatory human checkpoints, instead of the user hand-dispatching each agent.
when_to_use: >-
  Use when the user hands over a high-level goal to pursue with minimal per-step
  dispatch, or invokes the `goal` / `loop` commands. Opt-in and approval-gated —
  NEVER auto-invoked; announce it and get the plan approved before dispatching.
tools: Read, Grep, Glob, Bash
model: inherit
---

# Goal mode

## Goal

Let the kit orchestrate a multi-task goal end-to-end — bounded, gated, and
Linear-anchored — so the user sets direction instead of dispatching every agent.
This is a **special mode**, not the default: it runs only when explicitly invoked,
stops at checkpoints, and never takes an irreversible action on its own.

## Protocol

### 1. Frame the goal
- Run `spec-elicitation`: turn the goal into a spec with **EARS acceptance
  criteria** and explicit non-goals. If the goal is already concrete, confirm the
  criteria in one pass.

**Success criteria**
- The goal has explicit, testable acceptance criteria the loop can check against.

### 2. Plan and anchor the work
- Run `writing-plans` to break the goal into small tasks. Create/locate a Linear
  issue per task via `linear-router` (every issue has a project). Linear is the
  task source; the run ledger (see step 4) is ephemeral run-state only.

**Success criteria**
- Each task maps to a Linear issue with a project; the plan is granular enough to
  dispatch one task per lane.

### 3. CHECKPOINT 1 — approve the plan
- Present the spec, the task plan, and the run caps (max iterations, budget, max
  lanes). Do not dispatch anything until the user approves.

**Success criteria**
- No task is dispatched before explicit approval.

### 4. Dispatch a bounded batch
- Use `parallel-lanes` (one git worktree + one branch + one ticket per concurrent
  task) and `subagent-dispatch` (record BASE per task; keep the durable ledger).
  Respect the lane cap; queue the rest.

**Success criteria**
- Each lane is isolated (no shared-tree `git add -A`/checkout/reset); the run is
  reconstructable from the ledger alone.

### 5. Gate every task
- Each task's result goes through the post-implementation gate: `code-reviewer` +
  `spec-review`, then `verify-runtime`, plus matrix add-ons for the touched surface.

**Success criteria**
- No task is integrated without a green gate; a failed gate blocks that task.

### 6. CHECKPOINT 2 — approve before anything irreversible
- Before any merge, push, outward call, or destructive action, pause and get
  explicit approval. In checkpointed mode these never auto-execute.

**Success criteria**
- Nothing irreversible runs without approval in the same turn.

### 7. Integrate, persist state, and re-evaluate
- Integrate approved work via `pr-hygiene`. Re-check the goal against the acceptance
  criteria from step 1. Continue with the next batch, or stop.
- **Persist the compact state-of-goal.** Write/refresh `.neyra/goal-<id>/STATE.md`
  (goal / metric-this-round / done / open / drift) — a small, durable summary that
  survives context compaction. This is distinct from the per-task dispatch ledger:
  the ledger reconstructs *how*, STATE.md answers *where the goal stands* in one
  screen. Re-read it at the top of each iteration. **On Claude Code** the driver
  returns `stateOfGoal` ready to write; **on Cursor / Codex** (no driver) you derive
  the same fields yourself from the batch's results — the doc and its purpose are
  identical, only who computes it differs.
- **Honor the per-round observable.** A round is *productive* only if at least one
  task both advanced the goal and moved a real observable. On Claude Code the driver
  computes this (`productive`, from `advancesGoal` + a non-"none" observable); on
  Cursor / Codex you make the same call from each task's reported observable. Treat a
  non-productive round as a signal, not noise (see step 8).

**Success criteria**
- The goal is re-evaluated against its criteria each iteration, not assumed done.
- `STATE.md` reflects the latest round and is re-read before the next batch.

### 8. Stop and hand off
- Stop when: the goal meets its acceptance criteria; a cap is reached (iterations or
  budget); **two consecutive non-productive rounds** (no metric moved — spinning, not
  progressing); or a task is `BLOCKED` / `NEEDS_CONTEXT` with no safe next step. On
  stop, write a resumable summary: what landed, what remains, why it stopped.

**Success criteria**
- On stop, the state is resumable and the reason is explicit.
- A spinning loop stops on the non-productive heuristic instead of burning the iteration cap.

## Rules

- **Caps are hard:** `--max-iter` (default 5), `--budget` (tokens/$), `--lanes`
  (default 2, cap 4). Reaching a cap stops the loop; it does not silently continue.
- **Checkpoints 1 and 2 are mandatory** in checkpointed mode — never skip them.
- **Linear is the task source; the ledger is ephemeral** run-state under
  `.neyra/goal-<id>/` (gitignored). Never a second source of truth.
- **Every round needs an observable.** Each task reports the measurable it moved — a
  scalar delta when one exists, else an explicit binary/observable proxy (per
  `analytics-instrumentation` conventions). "Nothing moved" is a valid answer that
  marks the round non-productive; it is never silently skipped.
- **Re-anchor to the goal, not the brief.** A task that passes its own gate but does
  not advance the stated goal is drift — record it, don't integrate it as progress.
  (Claude Code's driver returns this as `advancesGoal: false`; on Cursor / Codex you
  make the same judgement per task.)
- **`BLOCKED` / `NEEDS_CONTEXT` → stop and escalate**, with a named cause.
- **Announce it:** state that goal-mode is active and name the current step each turn
  (the kit transparency rule applies to autonomous runs).
- **Hosts:** Claude Code may run the non-interactive batch (step 4–5) through the
  deterministic driver `agents/neyra-dev-kit/orchestration/goal-mode.workflow.js`;
  Cursor and Codex follow this protocol via their host `/loop`. Checkpoints happen in
  the main loop, between batches — the driver never merges or acts outward.
- **Anti-drift is host-neutral.** The per-round observable, goal re-anchor, compact
  `STATE.md`, and non-productive-round stop apply on all three tools. On Claude Code
  the driver *computes and enforces* them (schema-required fields + computed
  `productive`/`stateOfGoal`); on Cursor / Codex the agent produces the same signals
  by following steps 7–8. Same contract; only the enforcement mechanism differs.

## How to run

- **Claude Code:** `goal-mode: <your goal>` (or `/goal <goal>`). It frames the spec,
  plans, and stops at **checkpoint 1** for approval; on approval it runs the batch via
  the driver (`Workflow({ scriptPath: "agents/neyra-dev-kit/orchestration/goal-mode.workflow.js", args: { goal, lanes, tasks } })`),
  stops at **checkpoint 2** before integrating, then loops. `loop` resumes the active goal.
- **Cursor / Codex:** invoke this skill (`/goal-mode` or `@goal-mode`) and drive
  iterations with the host `/loop`; no driver — the batch runs as skill-guided steps.
- Full walkthrough + caps: `agents/neyra-dev-kit/orchestration/README.md`.
