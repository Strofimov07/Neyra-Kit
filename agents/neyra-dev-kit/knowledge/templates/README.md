# `docs/knowledge/` — knowledge graph (kit-scaffolded)

This repo treats durable knowledge as a **typed memory graph** (kit skill
`knowledge-graph`): typed nodes (`REQ`/`UXC` with Type Business/Functional/System/
UX-contract/NFR, `ADR`, `RSK`, `COMP`, `EVT`/`MET`, `RUN`), typed edges, one owner
per fact, a freshness contract, and a code→node bridge.

## Files (scaffolded by `install.sh`)
- `knowledge-map.yml` — code→node bridge (fill per repo).
- `memory_freshness.py` — cadence sweep over the agent's auto-memory layer.
- `check_code_node.py` — code→node check (changed git paths vs the manifest).
- `routines/doc-freshness.SKILL.md` — weekly freshness-sweep routine spec (register it).
- `MEMORY_GRAPH.md` / `MEMORY_OPERATIONS.md` — fill with this repo's canon map + ops
  (model is in the skill; these hold the repo-specific layer contract & migration).

## Triggers that keep docs fresh (skill `knowledge-graph` → Triggers)
1. **code→node** (DoD, primary) — change a mapped file → update its node.
2. **cadence sweep** — `memory_freshness.py` + canonical-hub review dates.
3. **issue-close → canon**.
4. **verify vs running system** — periodic check against staging/prod (code ships ahead of docs).
5. **skill auto-fire**.

> Canon writes are outward-facing — propose first, land after approval.
