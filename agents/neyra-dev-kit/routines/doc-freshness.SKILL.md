---
name: doc-freshness
description: Weekly doc/canon freshness sweep (memory + code→node + canonical hub review-dates)
---

Weekly documentation-freshness sweep for the repo at {{REPO_PATH}}. Calendar backstop
for the knowledge graph (see docs/knowledge/MEMORY_GRAPH.md / MEMORY_OPERATIONS.md).
Do NOT auto-edit the canon — report overdue / drift only.

Run three checks:
1. `cd {{REPO_PATH}} && python3 docs/knowledge/memory_freshness.py` — overdue memory nodes (last_verified vs cadence).
2. `cd {{REPO_PATH}} && python3 docs/knowledge/check_code_node.py` — code changes needing a canon-node update (code→node).
   No ref is passed on purpose: the script resolves the integration branch itself (`KNOWLEDGE_DIFF_BASE`, then `origin/HEAD`, then common names).
   A repo that integrates on a branch other than its default one sets `KNOWLEDGE_DIFF_BASE` — hardcoding a ref here is how this check silently
   measured one commit instead of a branch before.
3. If a Notion/wiki MCP is available: read the canonical hub configured for this repo and check each sub-hub's "Last Review" vs "Review Cadence"; list overdue. If unavailable (headless), note it and skip.

Report: per check, "OK" or bullets of overdue items with what to update; end with one line "update first: …". If all fresh, reply "freshness OK".
