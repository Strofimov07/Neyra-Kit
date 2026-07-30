#!/usr/bin/env python3
"""check_code_node.py — code→node freshness trigger (см. MEMORY_GRAPH.md §6).

Сверяет изменённые в git файлы с `knowledge-map.yml` (`code_to_node`): если
тронут mapped-файл, печатает узлы канона, которые надо обновить в том же
изменении. Это сильнейший event-триггер обновления документации (DoD: изменение
не закрыто, пока затронутые узлы не обновлены или явно не подтверждены).

Использование:
  python3 docs/knowledge/check_code_node.py                 # diff vs merge-base с интеграционной веткой (см. default_base())
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


def default_base():
    """Merge-base с интеграционной веткой репозитория.

    Порядок: явный KNOWLEDGE_DIFF_BASE → реальная default-ветка репозитория
    (origin/HEAD, если настроена) → распространённые имена. Раньше здесь было
    жёстко зашито `origin/main`: в репозитории, интегрирующемся на `dev` (или
    `master`), команда падала, скрипт молча откатывался на `HEAD~1` и показывал
    файлы одного последнего коммита вместо всей ветки — недооценивая дрейф.

    Определение через origin/HEAD снимает угадывание там, где оно настроено; список
    имён — best-effort fallback. Переопределяется переменной KNOWLEDGE_DIFF_BASE.
    """
    candidates = []
    env_base = os.environ.get("KNOWLEDGE_DIFF_BASE")
    if env_base:
        candidates.append(env_base)
    try:
        head = subprocess.check_output(
            ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if head:
            candidates.append(head)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    candidates += [
        "origin/main",
        "main",
        "origin/dev",
        "dev",
        "origin/master",
        "master",
    ]
    for ref in candidates:
        try:
            return subprocess.check_output(
                ["git", "merge-base", "HEAD", ref], text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return "HEAD~1"


def changed_files(args):
    if "--staged" in args:
        cmd = ["git", "diff", "--name-only", "--cached"]
    else:
        base = next((a for a in args if not a.startswith("-")), None)
        if not base:
            base = default_base()
        cmd = ["git", "diff", "--name-only", base]
    try:
        out = subprocess.check_output(cmd, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
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
        return [
            x.strip().strip('"').strip("'") for x in m.group(1).split(",") if x.strip()
        ]

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
    print(
        "  ⚠ mapped paths touched — update these canon nodes (and bump Last-verified):"
    )
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
