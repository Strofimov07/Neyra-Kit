---
name: doc-freshness
description: Weekly doc/canon freshness sweep (memory + code→node + hub review-dates + wiki host hygiene)
---

Weekly documentation-freshness sweep for the repo at {{REPO_PATH}}. Calendar backstop
for the knowledge graph (see docs/knowledge/MEMORY_GRAPH.md / MEMORY_OPERATIONS.md).
Do NOT auto-edit the canon — report overdue / drift only.

Run four checks:
1. `cd {{REPO_PATH}} && python3 docs/knowledge/memory_freshness.py` — overdue memory nodes (last_verified vs cadence).
2. `cd {{REPO_PATH}} && python3 docs/knowledge/check_code_node.py` — code changes needing a canon-node update (code→node).
   No ref is passed on purpose: the script resolves the integration branch itself (`KNOWLEDGE_DIFF_BASE`, then `origin/HEAD`, then common names).
   A repo that integrates on a branch other than its default one sets `KNOWLEDGE_DIFF_BASE` — hardcoding a ref here is how this check silently
   measured one commit instead of a branch before.
3. If a Notion/wiki MCP is available: read the canonical hub configured for this repo and check each sub-hub's "Last Review" vs "Review Cadence"; list overdue. If unavailable (headless), note it and skip.
4. Same MCP, wiki host hygiene: scan the operational pages (runbooks, deploy/ops hubs) for literal host addresses. The repository is covered by
   `check-repo-hygiene.py`; the wiki is not, and it is what someone reads before touching a server. A literal address belongs in exactly one host
   map; anywhere else the page should name the host and link that map. Report each page and address found — do not edit the canon.

Report: per check, "OK" or bullets of overdue items with what to update; end with one line "update first: …". If all fresh, reply "freshness OK".
