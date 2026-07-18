# neyra-dev-kit

**English** · [Русский](README.ru.md)

A portable discipline kit for AI coding agents (Claude Code, Cursor, Codex).
Install it into any git repository (or a plain workspace via
`--allow-non-git`) and it brings a set of **skills** (written procedures — how
to do a specific class of task correctly) and **subagents** (specialists that
activate at the right moment and apply those procedures) — so the agent
working in your repo follows the same discipline every time instead of
reinventing its process per task.

The kit is generic by construction: the **scoping rule** — a skill describes
*how*, your repo's `settings/` describes *what you have* (locales, your API
contract convention, your tracker workspace, metric sources, production
facts). Nothing product- or company-specific lives in the skill layers — a
linter (`lint-scope.py`) enforces this on every kit change.

> This repository is the canonical authoring and release source for the shared
> Neyra kits. Product repositories are consumers: their installed kit paths are
> generated and must not be used to author shared changes.

## Authoring and source policy

Shared skills, agents, hooks, installer code, governance, `VERSION`, decisions,
and evolution signals are changed here through a reviewed PR. Before editing a
shared path, run:

```bash
python3 agents/neyra-dev-kit/source-policy.py --require-canonical
```

The check requires both the root `.neyra-kit-canonical` marker and the canonical
GitHub origin. Consumer installs receive `.neyra-dev-kit.source` instead. A kit
problem found in a consumer is routed back to this repository through Kit
Evolution; installed copies are never promoted into a competing source.

## What's inside

- **26 engineering skills** (`agents/dev-skills/`) — the full cycle:
  requirements elicitation (spec-elicitation, EARS) → written plans →
  test-first implementation → systematic debugging → code review → contract
  safety → localization → release readiness → regression scouting → incident
  response → multi-agent orchestration (parallel lanes, subagent dispatch,
  goal mode) → evolving the kit itself.
- **9 product/growth role profiles** (`agents/product-skills/`) — discovery,
  research & insights, solution design, delivery planning, growth analytics,
  finance/business impact, finance intelligence, knowledge base, shared
  delivery base.
- **5 management skills** (`agents/mgmt-skills/`) — for senior leaders: a
  shared report skeleton (status-report-shape: RAG + metrics + owned
  hypotheses + self-eval of last cycle's hypotheses; no individual
  performance ratings), team health check (DORA / SPACE-lite / squad health /
  cost / reliability), delivery audit (investment distribution, diff-vs-ticket
  honesty check, stage bottleneck), portfolio PMO (dependency graph,
  deduplicated RAID register, gated batch planning), goals/OKR (falsifiable
  KRs, run-rate, both-direction challenge protocol, private personal mode).
- **Subagents** (`.claude/agents/`) — auto-invocable Claude Code wrappers
  around the skills, each with a minimal tool set.
- **Installer** (`agents/neyra-dev-kit/install.sh`) — copies the chosen kit
  into a target repository; templated subagents (`linear-router`,
  `localization-checker`, `contract-checker`) are rendered from your config.
  Idempotent — re-run any time to pull kit updates.
- **Hooks for three surfaces** (`agents/neyra-dev-kit/hooks/`) — one
  SessionStart/PreToolUse/PostToolUse/Stop logic for Claude Code, Cursor,
  and Codex.
- **Knowledge-graph layer** (`agents/neyra-dev-kit/knowledge/`) — keeps
  canonical docs from drifting away from the code they describe.

## Four kits, one installer

`install.sh <kit> <repo> <config>` — `kit` picks the set (default `dev`):

| Kit | Skills | For whom |
|---|---|---|
| **dev** | everything in `agents/dev-skills/` | engineers, any repository |
| **product** | 5 profiles from `agents/product-skills/` | PM / discovery work |
| **growth** | 2 profiles from `agents/product-skills/` | growth work |
| **mgmt** | everything in `agents/mgmt-skills/` | senior leaders: priorities, goals, effectiveness, portfolio (`--allow-non-git` — works in a notes workspace) |

Example configs: `agents/neyra-dev-kit/configs/_*.example.sh`.

## settings/ — your project scope

After installing, create `settings/` in your repository (template in this
repo's [settings/README.md](settings/README.md)): your install config,
`CONNECTORS.md` (metric sources for the mgmt kit — the paste/CSV → file → MCP
ladder), `facts/` (production signatures for incident-runbook), `brand.md`.
For goal-okr's personal mode — `settings/private/` (must be gitignored).

## Wiring MCP tools (Linear / Notion)

Some subagents reference MCP tools via `{{LINEAR_MCP_PREFIX}}` /
`{{NOTION_MCP_PREFIX}}` placeholders — MCP server ids are per-user. Set yours
in the install config (`LINEAR_MCP_PREFIX=...`, `NOTION_MCP_PREFIX=...` — find
them in Claude Code via `/mcp`) and `install.sh` substitutes them at install
time. Left empty, those tools are simply inactive for the subagent; everything
else works.

## Quick start

```bash
git clone git@github.com:Strofimov07/Neyra-Kit.git
cd Neyra-Kit/agents/neyra-dev-kit
cp configs/_product.example.sh configs/my-repo.sh   # fill in the fields
./install.sh dev /path/to/your-repo configs/my-repo.sh
./install.sh --dry-run ...   # preview without writing; --doctor — status check
```
