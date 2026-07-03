# Product skills — canonical source (multi-agent)

This directory is the **authoritative copy** of the product/growth/finance role profiles: each skill is a folder with `SKILL.md` (YAML frontmatter + Markdown body). The content is **agent-runtime–agnostic and product-agnostic**; individual tools mount or copy these folders into their own discovery paths, and the `product` / `growth` kits (see `agents/neyra-dev-kit/manifests/`) ship them to consumer repos.

> **Scoping rule.** These profiles are generic protocol — zero project facts (enforced by `agents/neyra-dev-kit/lint-scope.py`). Project-specific skill overlays (hardcoded paths, product domain packs — e.g. `aso-growth-system`) live in `settings/skills/` and never ship with a kit — see [settings/README.md](../../settings/README.md). **Engineering execution — build/QA, architecture, release — uses `agents/dev-skills/` directly**; the old `dev-qa` / `architecture` / `release` role profiles were retired (they only duplicated dev-skills). See the decisionLog.

| Skill | Purpose |
|--------|---------|
| [delivery-base](delivery-base/SKILL.md) | Shared delivery base: tracker/wiki sync, `AGENTS.md` precedence, role/task-anchor reporting |
| [product-discovery](product-discovery/SKILL.md) | Runtime profile for canonical Discovery / Problem Definition Agent |
| [product-research-insights](product-research-insights/SKILL.md) | Runtime profile for canonical Research & Insights Agent |
| [product-solution-design](product-solution-design/SKILL.md) | Runtime profile for canonical Solution & Design Agent |
| [product-delivery-planning](product-delivery-planning/SKILL.md) | Runtime profile for canonical Delivery Planning Agent |
| [growth-product-analytics](growth-product-analytics/SKILL.md) | Runtime profile for canonical Growth & Product Analytics Agent |
| [finance-business-impact](finance-business-impact/SKILL.md) | Runtime profile for canonical Finance & Business Impact Agent |
| [finance-intelligence](finance-intelligence/SKILL.md) | Runtime profile for canonical Finance Intelligence Agent (output contract, policy, delivery checklist) |
| [knowledge-memory-bank](knowledge-memory-bank/SKILL.md) | Runtime profile for canonical Knowledge & Memory Bank Agent |

**Do not** edit only under `.cursor/skills/` — those entries are symlinks to here.

See **[Multi-agent runtimes](../../docs/neyra-ai-skills/multi-agent-runtimes.md)** for Cursor, Codex, Claude Code, and other adapters.
