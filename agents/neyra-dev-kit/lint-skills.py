#!/usr/bin/env python3
"""Validate SKILL.md files against the canonical contract (SKILL_CONTRACT.md / NEB-1249).

One format, two runtimes (kit + AssistantUI). Pure stdlib — no YAML dep; tolerant
frontmatter parse (good enough for a linter, robust to folded `>-` scalars).

Usage: lint-skills.py [dir ...]   (default: agents/dev-skills agents/product-skills agents/mgmt-skills)
Exits non-zero if any skill violates the contract.
"""
import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TRIGGER_RE = re.compile(r"\b(use when|trigger with|trigger:|when )", re.IGNORECASE)
KNOWN_KEYS = {"name", "description", "when_to_use", "tools", "model",
              "requires_memory", "connectors"}


def split_frontmatter(text):
    """Return (frontmatter_str, top_level_keys) or (None, None) if no fenced block."""
    if not text.startswith("---"):
        return None, None
    end = text.find("\n---", 3)
    if end == -1:
        return None, None
    fm = text[3:end]
    # top-level keys = lines matching `^key:` (not indented continuation lines)
    keys = re.findall(r"(?m)^([A-Za-z_][\w-]*):", fm)
    return fm, keys


def value_of(fm, key):
    """Crude single-line value extractor for a top-level key."""
    m = re.search(r"(?m)^%s:[ \t]*(.*)$" % re.escape(key), fm)
    return m.group(1).strip() if m else None


def lint_file(path):
    errs, warns = [], []
    text = open(path, encoding="utf-8").read()
    fm, keys = split_frontmatter(text)
    if fm is None:
        return ["no '---' fenced frontmatter"], []
    keyset = set(keys)

    if "name" not in keyset:
        errs.append("missing `name`")
    else:
        name = value_of(fm, "name") or ""
        if not NAME_RE.match(name):
            errs.append("`name` not kebab-case: %r" % name)
        else:
            dirname = os.path.basename(os.path.dirname(path))
            if name != dirname:
                warns.append("`name` (%s) != dir (%s)" % (name, dirname))

    if "description" not in keyset:
        errs.append("missing `description`")
    else:
        # description may be a folded scalar; grab until the next top-level key
        m = re.search(r"(?ms)^description:(.*?)(?=^[A-Za-z_][\w-]*:|\Z)", fm)
        desc = (m.group(1) if m else "").strip()
        if len(desc) < 40:
            errs.append("`description` too short (<40 chars)")
        # NEB-1318: a description should say WHEN to load the skill, not narrate the
        # workflow step-by-step — else the model acts on the one-line summary and
        # never reads the body. Warn (don't fail) on procedural/ordinal language.
        if re.search(r"\b(step\s*\d|firstly|secondly|thirdly|and then)\b", desc, re.IGNORECASE):
            warns.append("description reads procedural (step/ordinal language) — prefer a pure 'when to load' trigger")

    # Trigger requirement: satisfied by a non-empty `when_to_use` field OR a
    # trigger phrase in the frontmatter (description).
    wtu = ""
    if "when_to_use" in keyset:
        m = re.search(r"(?ms)^when_to_use:(.*?)(?=^[A-Za-z_][\w-]*:|\Z)", fm)
        wtu = (m.group(1) if m else "").strip()
    if len(wtu) < 10 and not TRIGGER_RE.search(fm):
        errs.append("no trigger: add a `when_to_use` field or a 'use when / trigger with / when …' phrase to the description")

    for k in keyset:
        if k not in KNOWN_KEYS:
            warns.append("unknown key `%s`" % k)
    return errs, warns


def main(argv):
    root = os.getcwd()
    dirs = argv[1:] or ["agents/dev-skills", "agents/product-skills", "agents/mgmt-skills"]
    files = []
    for d in dirs:
        ad = os.path.join(root, d)
        if not os.path.isdir(ad):
            print("skip (not found): %s" % d)
            continue
        for entry in sorted(os.listdir(ad)):
            p = os.path.join(ad, entry, "SKILL.md")
            if os.path.isfile(p):
                files.append(p)

    n_fail = n_warn = 0
    for p in files:
        rel = os.path.relpath(p, root)
        errs, warns = lint_file(p)
        if errs:
            n_fail += 1
            print("FAIL %s" % rel)
            for e in errs:
                print("   ✗ %s" % e)
        elif warns:
            n_warn += 1
            print("ok   %s" % rel)
        for w in warns:
            print("   ! %s" % w)

    print("\n%d skills · %d failed · %d with warnings" % (len(files), n_fail, n_warn))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
