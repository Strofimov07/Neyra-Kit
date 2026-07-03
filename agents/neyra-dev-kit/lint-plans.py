#!/usr/bin/env python3
"""Lint implementation-plan artifacts for forbidden placeholders (NEB-1322).

A plan exists to close decisions before code is written. Placeholders reopen
them, so they are banned. Pure stdlib.

Usage: lint-plans.py [file-or-dir ...]   (default: docs/plans)
Exits non-zero if any plan contains a forbidden placeholder.
"""
import os
import re
import sys

# Forbidden placeholder patterns (case-insensitive, word-boundary where sensible).
FORBIDDEN = [
    r"\bTBD\b",
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bimplement later\b",
    r"\bsimilar to (task|the above)\b",
    r"\badd validation\b",
    r"\bwrite tests for the above\b",
]
PATTERNS = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN]


def lint_file(path):
    hits = []
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        for pat in PATTERNS:
            if pat.search(line):
                hits.append((i, pat.pattern, line.strip()))
    return hits


def gather(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                files += [os.path.join(root, n) for n in names if n.endswith(".md")]
        elif os.path.isfile(p):
            files.append(p)
    return files


def main(argv):
    paths = argv[1:] or ["docs/plans"]
    files = gather(paths)
    if not files:
        print("skip: no plan files found in %s" % ", ".join(paths))
        return 0
    n_fail = 0
    for f in files:
        hits = lint_file(f)
        if hits:
            n_fail += 1
            print("FAIL %s" % f)
            for ln, pat, text in hits:
                print("   ✗ line %d: forbidden placeholder %s — %r" % (ln, pat, text[:80]))
    print("\n%d plan files · %d with forbidden placeholders" % (len(files), n_fail))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
