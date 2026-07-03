# Management skills — canonical source (multi-agent)

Skill family for **senior engineering/product leaders** — the management cut
of the kit, alongside `dev-skills/` (execution discipline) and
`product-skills/` (product/growth role profiles). A manager's working surface
is priorities, goals, effectiveness, and a portfolio of projects — not a
codebase — so these install into a manager's workspace (git repo or, via
`--allow-non-git`, a plain notes/ops workspace) through the `mgmt` kit
(`agents/neyra-dev-kit/manifests/mgmt.sh`).

Same layering contract as every kit family: these files are **generic
protocol** — zero project facts (`lint-scope.py` enforces). Concrete metric
sources, thresholds, teams, and private data live in the consuming
workspace's `settings/` (`CONNECTORS.md`, `facts/`, `private/`).

| Skill | Purpose |
|--------|---------|
| [status-report-shape](status-report-shape/SKILL.md) | Shared report skeleton: RAG + metrics + risks + owned hypotheses + self-eval of prior hypotheses. No individual ratings — structural rule |
| [team-health-check](team-health-check/SKILL.md) | Recurring org-health report: DORA, SPACE-lite (team-level), squad-health self-assessment, infra cost, reliability/security |
| [delivery-audit](delivery-audit/SKILL.md) | Period audit: investment distribution, diff-vs-ticket honesty check, stage bottleneck, business-value lines, hygiene violations |
| [portfolio-pmo](portfolio-pmo/SKILL.md) | Cross-team portfolio: dependency graph, deduplicated RAID register, gated batch planning with mid-flight re-check, RAG rollup, live Q&A |
| [goal-okr](goal-okr/SKILL.md) | OKRs from strategy: falsifiable KRs (EARS), run-rate auto-status, both-direction challenge protocol, private personal mode with hard trust gates |

## Data flow

```
settings/CONNECTORS.md (paste/CSV → file → MCP, graceful degradation)
        │
        ▼
team-health-check ─┐
delivery-audit ────┼─► status-report-shape ─► page / email digest
portfolio-pmo ─────┘
goal-okr ──► tracker (anchored OKRs) + settings/private/ (personal mode only)
```

## Hard boundaries

- **No individual performance ratings in any report** (`status-report-shape`
  rule; SPACE/GitClear-documented antipattern).
- **Personal-mode data never leaves `settings/private/`** — gitignored, never
  installed, never published; candidate-not-verdict; draft-only outward;
  `trust-boundary-review` is a mandatory pre-check there.
- The tracker is the single register (RAID, OKR anchors) — no shadow docs.
