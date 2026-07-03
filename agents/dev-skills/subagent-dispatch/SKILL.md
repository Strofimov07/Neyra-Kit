---
name: subagent-dispatch
description: >-
  Dispatches a multi-task plan across fresh subagents with a compaction-proof
  protocol — a durable ledger, the BASE commit recorded per task, and a
  NEEDS_CONTEXT / BLOCKED status vocabulary with triage.
when_to_use: >-
  Use when delegating a multi-task plan to subagents or running parallel agents,
  and you need an auditable, resumable trail of who did what and why a task
  stalled. Pairs with writing-plans. For parallel (simultaneous) agents in the
  same repo, also use `parallel-lanes` for workspace isolation before dispatch.
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Subagent dispatch

## Goal

Run a plan across fresh-context subagents so the work is auditable and resumable
even after conversation compaction — without losing track of what each task did.

## Protocol

### 1. Keep a durable ledger

- Conversation memory does not survive compaction. Maintain a ledger file that
  records, per task: status, and on completion `commits <base7>..<head7>, review <verdict>`.

**Success criteria**
- The run's state is reconstructable from the ledger alone.

### 2. Record BASE before each dispatch

- Capture the BASE commit before dispatching a task (never assume `HEAD~1`), so
  the task's diff range is unambiguous.

**Success criteria**
- Every task has an exact, recorded commit range.

### 3. Dispatch one task, fresh context

- Give the subagent its task brief + the interfaces it needs from earlier tasks +
  the report contract — not the whole session history.

**Success criteria**
- The subagent has exactly what it needs, nothing more.

### 4. Handle status

- `NEEDS_CONTEXT` → re-dispatch with the missing information.
- `BLOCKED` → triage: missing context / flawed reasoning / scope too big / plan
  error → re-dispatch, escalate the model, break the task down, or escalate to a human.

**Success criteria**
- No task silently stalls; every block has a named cause and a next action.

## Rules

- The ledger is the source of truth for the run — update it as each task lands.
- One task per dispatch; do not bundle.
- Record the commit range from the recorded BASE, not from `HEAD~1`.
- Each task's result still goes through the post-implementation gate (`spec-review` + `code-reviewer` + `verify-runtime`).
