# settings/ — project-specific scope (yours to create)

**English** · [Русский](README.ru.md)

The kit's skill layers (`agents/dev-skills/`, `agents/product-skills/`,
`agents/mgmt-skills/`) are **generic protocol** — they never contain your
project's facts. Everything specific to *your* workspace lives in a
`settings/` directory **in your repo** (not in this kit):

| Path | What lives there | Consumed by |
|---|---|---|
| `settings/configs/<repo>.sh` | your install config (copy from `agents/neyra-dev-kit/configs/_*.example.sh`) | `install.sh` |
| `settings/CONNECTORS.md` | your metric sources for the mgmt kit (ladder: paste/CSV → file → MCP; copy `CONNECTORS.example.md`) | team-health-check, delivery-audit, portfolio-pmo, goal-okr |
| `settings/skills/<id>/SKILL.md` | a project-owned Claude skill (kit never authors these; source of truth) — generated into `.claude/skills/<id>/` | `install.sh` (→ `.claude/skills/`) |
| `settings/mcp/<name>.mcp.json.tmpl` | a project MCP server declaration (static JSON; `${ENV}` placeholders expanded by Claude Code) — jq-merged into `.mcp.json` | `install.sh` (→ `.mcp.json`) |
| `settings/facts/` | your production facts (e.g. `incident-runbook.md` — known failure signatures) | incident-runbook |
| `settings/brand.md` | your naming/brand rules | anything writing user-facing copy |
| `settings/private/` | **gitignore this** — goal-okr personal-mode data (personal KRs, evidence trails, plan drafts). Never committed, never shared | goal-okr personal mode only |

The one-line rule: *would this line be true in a stranger's repo?* If yes, it
belongs in a skill (upstream, via issue/PR to the kit). If no, it belongs
here.

This directory in the kit repo carries only examples — your real `settings/`
lives in your repository.
