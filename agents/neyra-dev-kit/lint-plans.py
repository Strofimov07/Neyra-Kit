#!/usr/bin/env python3
"""Lint implementation-plan artifacts for forbidden placeholders (NEB-1322).

A plan exists to close decisions before code is written. Placeholders reopen
them, so they are banned. Pure stdlib.

The bare tokens (TODO / TBD / FIXME) match case-SENSITIVELY: the placeholder
convention is upper-case, while `Todo` is a Linear status name that task-anchor
prose legitimately uses ("remains `Todo`"). NEB-1800: matching it case-insensitively
kept a consumer's doctor red on 26 plan docs, and an always-red gate stops being a
gate. The phrase patterns stay case-insensitive.

Usage: lint-plans.py [file-or-dir ...]   (default: docs/plans)
Exits non-zero if any plan contains a forbidden placeholder.
"""
import os
import re
import sys

# Forbidden placeholder patterns: (regex, flags). Bare tokens are case-sensitive
# (see module docstring); phrases are case-insensitive.
FORBIDDEN = [
    (r"\bTBD\b", 0),
    (r"\bTODO\b", 0),
    (r"\bFIXME\b", 0),
    (r"\bimplement later\b", re.IGNORECASE),
    (r"\bsimilar to (task|the above)\b", re.IGNORECASE),
    (r"\badd validation\b", re.IGNORECASE),
    (r"\bwrite tests for the above\b", re.IGNORECASE),
]
PATTERNS = [re.compile(p, flags) for p, flags in FORBIDDEN]


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
