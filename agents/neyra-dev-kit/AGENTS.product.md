<!-- neyra-dev-kit governance fragment — product kit. Rendered by install.sh.
     Include this file from the repo's AGENTS.md / CLAUDE.md. Do not hand-edit the
     rendered copy — change it in the kit and re-run install. -->

# Neyra product-kit — execution governance ({{REPO_NAME}})

This repo uses the shared Neyra product skill stack. Skills live under
`agents/product-skills/` (canonical specs) and are surfaced as auto-invocable
subagents under `.claude/agents/`. The skill is the spec; the subagent is the
auto-trigger surface — invoke whichever the runtime supports.

## Core discipline: problem before solution
Every significant output — spec, story, discovery doc — MUST state the user problem
and evidence before proposing a solution. "Open questions" sections are mandatory
until explicitly resolved and recorded.

## Default skill flow (most product tasks)
`product-research-insights` (evidence/synthesis, when the problem needs research) →
`product-discovery` → `product-solution-design` →
`product-delivery-planning`, with `knowledge-memory-bank` as the
memory layer throughout.

## Skill ↔ subagent map
| neyra-skill | subagent | fires on |
|---|---|---|
| product-research-insights | _(apply inline)_ | evidence gathering, synthesis, JTBD/pain-point analysis before framing |
| product-discovery | product-brainstormer | discovery, user-problem framing, opportunity sizing |
| product-solution-design | solution-designer | solution ideation, feature spec, cross-app contract design |
| product-delivery-planning | delivery-planner | epic/story breakdown, DoR check, sprint planning |
| knowledge-memory-bank | _(apply inline)_ | decision logging, context persistence |

## Definition of Ready (DoR) — every story before dev starts
1. Problem statement with user evidence.
2. Solution bounded to a single deliverable.
3. Acceptance criteria (observable, testable).
4. Open questions listed and either resolved or explicitly deferred.
5. Linear issue present with a project set — workspace: {{LINEAR_WORKSPACE}}.

## Transparency rule (mandatory in autonomous, delegated, and `/loop` runs)
- Every turn names the active skill(s)/subagent(s) it used or assumed, and why.
- Open questions must not silently become decisions — surface them explicitly.
- Skipping a skill gate is allowed only with an explicit one-line reason in the same turn.

## Repo facts (used by the subagents)
- Stack: {{STACK}}
- Build / verify command: `{{BUILD_VERIFY_CMD}}`
- Locales: {{LOCALES}}
- Typed-contract convention: {{CONTRACT_STACK}}
- Linear workspace: {{LINEAR_WORKSPACE}} (every issue MUST have a project — see `linear-router`).

<!-- kit-version: 0.4.0 -->
