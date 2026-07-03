# Connectors — <your workspace>

Concrete data sources for the mgmt-skills connector ladder (**paste/CSV →
file → MCP**, graceful degradation — a missing connector never blocks a
report, it renders as a visible gap). Generic contract lives in
`agents/mgmt-skills/status-report-shape/SKILL.md`; this file is your
project-specific list. Copy to `settings/CONNECTORS.md` and fill in.

| Source | Connector | Status | Used by |
|---|---|---|---|
| Tracker (issues, projects, cycle timestamps, RAID labels) | e.g. Linear/Jira MCP | ❌ fill in | delivery-audit, portfolio-pmo, goal-okr, team-health-check |
| Docs/wiki (strategy anchors) | e.g. Notion/Confluence MCP | ❌ fill in | goal-okr, portfolio-pmo |
| VCS + CI (PRs, diffs, deploys → DORA) | e.g. `gh` CLI | ❌ fill in | delivery-audit, team-health-check |
| Cloud billing (infra cost) | — | ❌ manual: paste/CSV export | team-health-check |
| Incidents / vulns | — | ❌ manual: paste from tracker/scanner | team-health-check |
| Team satisfaction (👍👎 + freetext) | — | ❌ manual: paste from chat | team-health-check |
| Squad-health self-assessment | — | ❌ manual: paste survey results | team-health-check |

Upgrade order (evidence bar per `status-report-shape`): a source earns an MCP
connector after 2+ manual cycles prove the report is actually read.
