#!/usr/bin/env python3
"""memory_freshness.py — freshness gate for an agent's auto-memory layer.

Part of the knowledge-graph freshness engine (skill `knowledge-graph`). Reads each
memory file's frontmatter (`last_verified`, `cadence`) and reports nodes that are
overdue or have no freshness fields. Pure stdlib.

Memory dir resolution (first that works):
  1. $CLAUDE_MEMORY_DIR
  2. derived from CWD: ~/.claude/projects/<cwd-with-/-as-->/memory
  3. first positional arg

Default cadence by node type when `cadence` is unset:
  project=30d, reference=90d, feedback=180d, user=180d. `on-change` never expires.

Usage:
  python3 memory_freshness.py                 # auto-resolve dir
  python3 memory_freshness.py <dir>           # explicit dir
  CLAUDE_MEMORY_DIR=/path python3 memory_freshness.py
  --strict   → exit 1 if overdue OR missing-fields (for a gate)

Exit: 0 fresh; 1 overdue (or, with --strict, missing fields); 2 dir not found.
"""

import os
import re
import sys
from datetime import date, datetime

DEFAULT_CADENCE_DAYS = {"project": 30, "reference": 90, "feedback": 180, "user": 180}
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def resolve_dir(args):
    pos = next((a for a in args if not a.startswith("-")), None)
    if pos:
        return os.path.expanduser(pos)
    env = os.environ.get("CLAUDE_MEMORY_DIR")
    if env:
        return os.path.expanduser(env)
    enc = os.getcwd().replace("/", "-")
    return os.path.expanduser(f"~/.claude/projects/{enc}/memory")


def parse_frontmatter(text):
    m = FM_RE.match(text)
    fm = {}
    if not m:
        return fm
    for line in m.group(1).splitlines():
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        k, _, v = s.partition(":")
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def cadence_days(fm):
    c = (fm.get("cadence") or "").lower()
    if c in ("on-change", "on_change", "manual"):
        return None
    m = re.match(r"(\d+)\s*d", c)
    if m:
        return int(m.group(1))
    return DEFAULT_CADENCE_DAYS.get(fm.get("type", ""), 90)


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    mem_dir = resolve_dir(args)
    if not os.path.isdir(mem_dir):
        print(f"memory dir not found: {mem_dir} (set CLAUDE_MEMORY_DIR)", file=sys.stderr)
        return 2

    today = date.today()
    overdue, missing, fresh = [], [], []
    for name in sorted(os.listdir(mem_dir)):
        if not name.endswith(".md") or name == "MEMORY.md":
            continue
        fm = parse_frontmatter(open(os.path.join(mem_dir, name), encoding="utf-8").read())
        lv = fm.get("last_verified")
        if not lv:
            missing.append(name)
            continue
        try:
            lvd = datetime.strptime(lv, "%Y-%m-%d").date()
        except ValueError:
            missing.append(f"{name} (bad last_verified: {lv})")
            continue
        cd = cadence_days(fm)
        age = (today - lvd).days
        if cd is not None and age > cd:
            overdue.append(f"{name} — {age}d (cadence {cd}d, verified {lv})")
        else:
            fresh.append(name)

    print(f"memory freshness @ {today} · {mem_dir}")
    print(f"  fresh:   {len(fresh)}")
    print(f"  overdue: {len(overdue)}")
    for x in overdue:
        print(f"    ⚠ {x}")
    print(f"  no freshness fields: {len(missing)}")
    for x in missing:
        print(f"    · {x}")

    if overdue or (strict and missing):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
