<!-- neyra-dev-kit bootstrap core (v1). Force-injected at session start by
     hooks/session-start.sh so the agent knows the kit exists and its gates are
     mandatory from turn one — instead of relying on the model choosing to read
     AGENTS.md. Keep this COMPACT (it is injected into every session). Canonical
     detail lives in AGENTS.md + AGENTS.neyra-devkit.md; this is the trigger layer. -->

# You have the Neyra dev-kit — read this first

This repo has an installed copy of the shared Neyra engineering skill stack:
`agents/dev-skills/`, surfaced as auto-invocable subagents in `.claude/agents/`.
These are **mandatory workflows, not suggestions.** Full spec: AGENTS.md.

## Shared-kit source boundary

The only canonical authoring source is
`git@github.com:Strofimov07/Neyra-Kit.git`. Before changing a shared kit path,
run `python3 agents/neyra-dev-kit/source-policy.py --require-canonical`. Failure
in a consumer is expected: route the signal to the Neyra Skills Kit Linear
project and do not hand-edit generated kit files. Project facts under
`settings/` remain owned by this repo.

## Rule of relevance (the 1% rule)

If there is even a ~1% chance a skill applies to what you're doing, invoke it —
this is not a judgement call you get to skip. "I already know how", "it's a
small change", "I'll do it at the end" are not reasons to skip a skill; they are
the exact moments skills exist for. When you invoke one, say so in one line:
"Using `<skill>` to `<purpose>`."

## Before declaring any code slice done — the gate is required

1. `code-reviewer` (simplify-diff) — reuse, scope, redundancy
2. matrix add-ons for the touched surface — `contract-checker` (endpoints),
   `localization-checker` (user-facing copy), `analytics-instrumentation`
   (behavior/funnel), `design-system-conformance` (UI), `migration-safety`
   (schema migrations), `security-reviewer` (auth / crypto / secrets /
   untrusted input / raw SQL / HTML / WebView / deep links)
3. `verify-runtime` — strongest practical check on the **real** surface
4. `release-readiness` + `regression-scout` for high-risk / cross-layer changes

Skip a required step only with an explicit one-line reason in the same turn
(e.g. "no runtime here, deferred verify-runtime").

## For logic and bug fixes — test first

Write a failing test that encodes the intended behavior (RED) before changing
implementation, make it pass (GREEN), then refactor. A bug fix with no
reproduction test is not done. Skill: `test-first`.

## Transparency (autonomous / delegated / `/loop` runs)

Each turn, name the skill(s)/subagent(s) you used or assumed and why — per step,
not only at the end. Distinguish what was verified from what is still assumed; a
green subagent report does not replace the gate's required final checks.

## Insight capture — log it the moment you hit it

Any kit friction found mid-work (a missing rule, a skill that misfired or was
absent, a gate skipped, a repeated correction) is persisted in the same turn.
In canonical Neyra-Kit, append one line to `agents/neyra-dev-kit/signals.log`.
In a consumer, write it to the Neyra Skills Kit Linear project after dedup (or
local-only `.neyra/kit-evolution-pending.log` when Linear is unavailable) and
report the sync debt. Never append to an installed shared-kit copy.

## Parallel agents — workspace isolation (mandatory)

When two or more agents run in the same repo at the same time, each MUST have its
own git worktree (`git worktree add`) or at minimum its own branch, and MUST stage
only explicit paths — never `git add -A`. Never run `git checkout`, `git stash`, or
`git reset --hard` in a tree a sibling is using. Use the `parallel-lanes` skill
before dispatching parallel work.

## Knowledge freshness — keep docs/canon current

The wiki/canon is a typed memory graph (skill `knowledge-graph`). Triggers that fire
a doc update: **code→node** (DoD — when you change a file mapped in
`docs/knowledge/knowledge-map.yml`, update its canon node in the same change),
**issue-close→canon**, and a weekly **freshness sweep**. If a weekly doc-freshness
routine isn't registered for this repo, register it from the staged spec
`docs/knowledge/routines/doc-freshness.SKILL.md`.

## Autonomous goal mode (opt-in only)

`goal-mode` lets the kit drive a goal end-to-end (decompose → dispatch → gate →
integrate → loop) instead of hand-dispatching each agent. It is **never
auto-invoked** — only on an explicit `goal` / `loop` request. When active: caps are
hard (max-iter / budget / lanes), the plan is approved at **checkpoint 1**, nothing
merges or acts outward without **checkpoint 2**, tasks run in isolated lanes
(`parallel-lanes`), and Linear is the task source. Skill: `goal-mode`.

## Linear hygiene

Every Linear issue MUST have a project, routed by stream. No project = not ready.
