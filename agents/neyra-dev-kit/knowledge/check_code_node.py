#!/usr/bin/env python3
"""check_code_node.py — code→node freshness trigger (см. MEMORY_GRAPH.md §6).

Сверяет изменённые в git файлы с `knowledge-map.yml` (`code_to_node`): если
тронут mapped-файл, печатает узлы канона, которые надо обновить в том же
изменении. Это сильнейший event-триггер обновления документации (DoD: изменение
не закрыто, пока затронутые узлы не обновлены или явно не подтверждены).

Использование:
  python3 docs/knowledge/check_code_node.py                 # diff vs merge-base origin/main (fallback HEAD~1)
  python3 docs/knowledge/check_code_node.py <base_ref>      # diff vs указанный ref
  python3 docs/knowledge/check_code_node.py --staged        # только staged-файлы
  --strict  → exit 1, если есть затронутые узлы (для гейта/CI)

Pure stdlib. Параметры пути: запускать из корня репо (где docs/knowledge/).
"""

import fnmatch
import os
import re
import subprocess
import sys

MAP = os.path.join(os.path.dirname(__file__), "knowledge-map.yml")


def changed_files(args):
    if "--staged" in args:
        cmd = ["git", "diff", "--name-only", "--cached"]
    else:
        base = next((a for a in args if not a.startswith("-")), None)
        if not base:
            try:
                base = subprocess.check_output(["git", "merge-base", "HEAD", "origin/main"], text=True).strip()
            except subprocess.CalledProcessError:
                base = "HEAD~1"
        cmd = ["git", "diff", "--name-only", base]
    try:
        out = subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e}", file=sys.stderr)
        return []
    return [l.strip() for l in out.splitlines() if l.strip()]


def parse_map(path):
    """Минимальный парсер code_to_node: каждый '- paths: [...]' с 'nodes:'/'also_check:'."""
    if not os.path.isfile(path):
        print(f"knowledge-map not found: {path}", file=sys.stderr)
        return []
    text = open(path, encoding="utf-8").read()
    section = text.split("code_to_node:", 1)
    if len(section) < 2:
        return []
    body = section[1]
    entries = re.split(r"\n\s*-\s+paths:", body)[1:]
    rules = []

    def arr(label, blk):
        m = re.search(rf"{label}:\s*\[(.*?)\]", blk, re.DOTALL)
        if not m:
            return []
        return [x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()]

    for e in entries:
        blk = "paths:" + e
        rules.append(
            {
                "paths": arr("paths", blk),
                "nodes": arr("nodes", blk),
                "also_check": arr("also_check", blk),
            }
        )
    return rules


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    files = changed_files(args)
    rules = parse_map(MAP)
    hits = []
    for f in files:
        for r in rules:
            if any(fnmatch.fnmatch(f, g) for g in r["paths"]):
                hits.append((f, r["nodes"], r["also_check"]))

    print(f"code→node check · {len(files)} changed files · {len(rules)} mapping rules")
    if not hits:
        print("  no mapped paths touched — no canon node update required by manifest.")
        return 0
    print("  ⚠ mapped paths touched — update these canon nodes (and bump Last-verified):")
    seen = set()
    for f, nodes, also in hits:
        extra = f" (+also: {', '.join(also)})" if also else ""
        print(f"    {f} → {', '.join(nodes)}{extra}")
        seen.update(nodes)
        seen.update(also)
    print(f"  nodes to review: {', '.join(sorted(seen))}")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main())
