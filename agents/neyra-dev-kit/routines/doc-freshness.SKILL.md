---
name: doc-freshness
description: Weekly doc/canon freshness sweep (memory + code→node + canonical hub review-dates)
---

Weekly documentation-freshness sweep for the repo at {{REPO_PATH}}. Calendar backstop
for the knowledge graph (see docs/knowledge/MEMORY_GRAPH.md / MEMORY_OPERATIONS.md).
Do NOT auto-edit the canon — report overdue / drift only.

Run three checks:
1. `cd {{REPO_PATH}} && python3 docs/knowledge/memory_freshness.py` — overdue memory nodes (last_verified vs cadence).
2. `cd {{REPO_PATH}} && python3 docs/knowledge/check_code_node.py origin/main` — code changes needing a canon-node update (code→node).
3. If a Notion/wiki MCP is available: read the canonical hub configured for this repo and check each sub-hub's "Last Review" vs "Review Cadence"; list overdue. If unavailable (headless), note it and skip.

Report: per check, "OK" or bullets of overdue items with what to update; end with one line "update first: …". If all fresh, reply "freshness OK".
