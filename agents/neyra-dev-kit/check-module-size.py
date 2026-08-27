#!/usr/bin/env python3
"""Modularity drift: oversized modules and tests coupled to private symbols.

Two structural signals that precede a painful refactor, neither of which any
prose gate catches:

1. A module that keeps growing. Nobody decides to write a 15k-line file; it
   accretes. By the time it hurts (merge conflicts on every PR, a second
   developer blocked) the split costs weeks.
2. Tests patching a module's *private* symbols. Each such patch is an edge
   pinning the internals of that module from the outside — the real cost of a
   later split, and invisible in any single diff.

Advisory by default (exit 0, prints what it found); --strict makes violations
fail. Thresholds are arguments, not policy: pick them per repo.

Usage:
  check-module-size.py [paths ...] [--max-lines N] [--top N] [--strict]
                       [--tests-dir DIR ...]
"""
import argparse
import os
import re
import subprocess
import sys

SRC_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".swift", ".kt", ".go", ".rb", ".java", ".cs", ".php", ".rs"}
SKIP_DIRS = {".git", "node_modules", "dist", "build", "out", ".next", "vendor", "venv", ".venv",
             "__pycache__", "migrations", "coverage", ".mypy_cache", ".pytest_cache"}

# Patching a symbol whose name starts with "_" — the outside reaching into internals.
PRIVATE_PATCH_RES = [
    re.compile(r"""patch\(\s*['"][\w.]+\.(_\w+)['"]"""),          # patch("mod._helper")
    re.compile(r"""patch\.object\(\s*[\w.]+\s*,\s*['"](_\w+)['"]"""),
    re.compile(r"""monkeypatch\.setattr\(\s*[\w.]+\s*,\s*['"](_\w+)['"]"""),
    re.compile(r"""(?:vi|jest)\.spyOn\(\s*[\w.]+\s*,\s*['"](_\w+)['"]"""),
]


def tracked_files(root):
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                             capture_output=True, text=True, check=True).stdout
        return [f for f in out.split("\0") if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        found = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                found.append(os.path.relpath(os.path.join(dirpath, fn), root))
        return found


def is_source(rel):
    parts = rel.split(os.sep)
    if any(p in SKIP_DIRS for p in parts):
        return False
    return os.path.splitext(rel)[1] in SRC_EXT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--max-lines", type=int, default=1500)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--tests-dir", action="append", default=[])
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    root = a.paths[0] if a.paths else "."
    files = [f for f in tracked_files(root) if is_source(f)]
    if not files:
        print("check-module-size: no source files found — nothing to check")
        return 0

    sizes = []
    for rel in files:
        p = os.path.join(root, rel)
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                sizes.append((sum(1 for _ in fh), rel))
        except OSError:
            continue
    sizes.sort(reverse=True)

    over = [(n, f) for n, f in sizes if n > a.max_lines]
    print("── module size (threshold %d lines)" % a.max_lines)
    for n, f in sizes[:a.top]:
        mark = "OVER " if n > a.max_lines else "     "
        print("  %s%6d  %s" % (mark, n, f))
    if over:
        print("  %d module(s) over threshold — a split gets more expensive every week" % len(over))

    # private-symbol coupling from tests
    test_dirs = a.tests_dir or [d for d in ("tests", "test", "__tests__", "spec") if os.path.isdir(os.path.join(root, d))]
    hits = {}
    for rel in files:
        if not any(rel.startswith(d + os.sep) or ("/%s/" % d) in rel for d in test_dirs):
            continue
        p = os.path.join(root, rel)
        try:
            text = open(p, "r", encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for rx in PRIVATE_PATCH_RES:
            for m in rx.finditer(text):
                hits.setdefault(m.group(1), set()).add(rel)

    print("── tests patching private symbols (dirs: %s)" % (", ".join(test_dirs) or "none found"))
    if not hits:
        print("  none")
    else:
        ranked = sorted(hits.items(), key=lambda kv: -len(kv[1]))
        total = sum(len(v) for v in hits.values())
        for sym, fs in ranked[:a.top]:
            print("  %-40s %d test file(s)" % (sym, len(fs)))
        print("  %d private symbol(s) pinned from %d test file(s) — each one is an edge to unpick on a split"
              % (len(hits), len({f for fs in hits.values() for f in fs})))
        print("  total patch sites (symbol × file): %d" % total)

    if a.strict and (over or hits):
        print("check-module-size: FAIL (--strict)")
        return 1
    print("check-module-size: advisory (use --strict to fail)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
