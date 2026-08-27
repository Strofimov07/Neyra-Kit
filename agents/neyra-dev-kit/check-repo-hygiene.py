#!/usr/bin/env python3
"""Onboarding hygiene: traps a repository sets for the next person who joins.

Each check is a class of defect that reads as harmless to the author and as an
instruction to a newcomer:

1. Host addresses in tracked documentation — a decommissioned address in a
   runbook sends someone to connect to a machine that is no longer yours.
2. Build artifacts in the index — a stale committed bundle is what tooling
   mounts and serves, so the repo shows an old build with no failing signal.
3. gitignore directory traps — a directory ignored while files inside it are
   tracked: existing files keep working, new ones are silently never added.
4. Broken relative links in tracked markdown — documentation pointing at files
   that no longer exist, i.e. instructions for a system that is gone.

Advisory by default; --strict fails. Nothing here is project-specific.

Usage: check-repo-hygiene.py [repo] [--strict] [--docs-glob PATTERN ...]
"""
import argparse
import ipaddress
import os
import re
import subprocess
import sys

IP_RE = re.compile(r"(?<![\w.])(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?![\w.])")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#?\s]+)")
ARTIFACT_DIRS = ("dist/", "build/", "out/", ".next/", "coverage/", "node_modules/", ".output/")
DOC_EXT = (".md", ".mdx", ".rst", ".txt")
# Documentation may legitimately show example addresses; these are reserved for docs.
DOC_SAFE = ("192.0.2.", "198.51.100.", "203.0.113.")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.repo)

    r = git(root, "ls-files", "-z")
    if r.returncode != 0:
        print("check-repo-hygiene: not a git repository — skipping")
        return 0
    tracked = [f for f in r.stdout.split("\0") if f]
    findings = 0

    # 1. host addresses in tracked docs
    print("── host addresses in tracked documentation")
    hits = []
    for rel in tracked:
        if not rel.lower().endswith(DOC_EXT):
            continue
        try:
            text = open(os.path.join(root, rel), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in IP_RE.finditer(line):
                val = m.group(1)
                if val.startswith(DOC_SAFE):
                    continue
                try:
                    ip = ipaddress.ip_address(val)
                except ValueError:
                    continue
                if ip.is_loopback or ip.is_unspecified or ip.is_multicast:
                    continue
                hits.append((rel, lineno, val))
    if hits:
        findings += len(hits)
        for rel, lineno, val in hits[:10]:
            print("  %s:%d: %s" % (rel, lineno, val))
        if len(hits) > 10:
            print("  … %d more" % (len(hits) - 10))
        print("  verify each address still belongs to you; a dead one is a wrong-machine instruction")
    else:
        print("  none")

    # 2. build artifacts in the index
    print("── build artifacts tracked in git")
    art_files = [rel for rel in tracked if any(("/" + rel).find("/" + d) >= 0 for d in ARTIFACT_DIRS)]
    if art_files:
        findings += 1
        print("  %d tracked file(s) under build-output paths, e.g.:" % len(art_files))
        for rel in art_files[:5]:
            print("    %s" % rel)
        print("  a committed build goes stale silently and is what tooling serves")
    else:
        print("  none")

    # 3. gitignore directory traps
    print("── ignored directories that still contain tracked files")
    gi = os.path.join(root, ".gitignore")
    traps = []
    if os.path.isfile(gi):
        for raw in open(gi, encoding="utf-8", errors="ignore").read().splitlines():
            pat = raw.strip()
            if not pat or pat.startswith("#") or pat.startswith("!") or "*" in pat:
                continue
            d = pat.rstrip("/").lstrip("/")
            if not d or not os.path.isdir(os.path.join(root, d)):
                continue
            inside = [f for f in tracked if f == d or f.startswith(d + "/")]
            if inside:
                traps.append((d, len(inside)))
    if traps:
        findings += len(traps)
        for d, n in traps:
            print("  %s/ is ignored but %d file(s) inside are tracked — new files there are silently never added" % (d, n))
    else:
        print("  none")

    # 4. broken relative links in tracked markdown
    print("── broken relative links in tracked markdown")
    broken = []
    tracked_set = set(tracked)
    for rel in tracked:
        if not rel.lower().endswith((".md", ".mdx")):
            continue
        base = os.path.dirname(rel)
        try:
            text = open(os.path.join(root, rel), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith(("//", "#", "{{")):
                continue
            resolved = os.path.normpath(os.path.join(base, target)) if not target.startswith("/") else target.lstrip("/")
            if resolved in tracked_set or os.path.exists(os.path.join(root, resolved)):
                continue
            broken.append((rel, target))
    if broken:
        findings += len(broken)
        for rel, target in broken[:10]:
            print("  %s → %s" % (rel, target))
        if len(broken) > 10:
            print("  … %d more" % (len(broken) - 10))
        print("  documentation pointing at files that no longer exist describes a system that is gone")
    else:
        print("  none")

    if a.strict and findings:
        print("check-repo-hygiene: FAIL (--strict), %d finding(s)" % findings)
        return 1
    print("check-repo-hygiene: %d finding(s) — advisory (use --strict to fail)" % findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
