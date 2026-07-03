<!-- neyra-dev-kit governance fragment — mgmt kit. Rendered by install.sh.
     Include this file from the workspace's AGENTS.md / CLAUDE.md. Do not
     hand-edit the rendered copy — change it in the kit and re-run install. -->

# Neyra mgmt-kit — management governance ({{REPO_NAME}})

This workspace uses the management skill stack — tooling for a senior leader's
working surface: priorities, goal-setting, effectiveness, and the project
portfolio. Skills live under `agents/mgmt-skills/` (canonical specs) and are
surfaced as auto-invocable subagents under `.claude/agents/`.

## Core discipline: sourced numbers, owned hypotheses, self-eval
Every recurring report follows `status-report-shape`: numbers carry sources
(paste/CSV → file → MCP ladder, missing data is visible, never invented),
every 🟡/🔴 gets ranked hypotheses with owners, and last cycle's hypotheses
are graded before new ones are written.

## Skill ↔ subagent map
| mgmt-skill | subagent | fires on |
|---|---|---|
| team-health-check | team-health-check | org/team health report, weekly pulse, monthly deep report |
| delivery-audit | delivery-audit | "what did the team ship", period review, investment distribution |
| portfolio-pmo | portfolio-pmo | cross-team planning, dependencies, RAID review, portfolio status |
| goal-okr | goal-okr | OKR set/update/grade, run-rate, goal challenge, 1:1 personal goals |
| status-report-shape | _(called by the above)_ | rendering stage of any recurring report |

## Hard boundaries (non-negotiable)
- **No individual performance ratings in any report.** Team-level rollups
  only; activity metrics never rank people.
- **Personal mode (goal-okr) is physically private**: data only under
  `settings/private/` (gitignored); candidate-not-verdict; draft-only outward;
  nothing about a person is ever sent or written to an external system.
- **The tracker is the single register** — OKR anchors and the RAID log live
  as tracker items; every issue has a project.

## Transparency rule
- Every turn names the active skill(s)/subagent(s) used or assumed, and why.
- Distinguish sourced numbers from estimates; missing connectors are reported,
  not papered over.

## Workspace facts (used by the subagents)
- Tracker workspace: {{LINEAR_WORKSPACE}} (routing: {{LINEAR_ROUTING}})
- Metric sources / connectors: see `settings/CONNECTORS.md`
- Reporting cadence: weekly pulse + monthly deep report (adjust per team)

<!-- kit-version: 0.12.0 -->
