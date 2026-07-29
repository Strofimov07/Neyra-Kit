#!/usr/bin/env python3
"""Fail on a dev-skill reference to an AGENTS.md section that does not resolve (NEB-1591).

Skills route work to named sections of the kit governance doc (e.g. "the
`Self-Improvement Rule` in AGENTS.md"). If the named section doesn't exist in the
governance the kit actually ships (templates/AGENTS.include.md.tmpl, rendered into a
consumer's AGENTS.neyra-devkit.md), the routing silently no-ops — a dead cross-file
anchor no other linter catches (lint-skills checks frontmatter, check-skill-mapping the
skill↔subagent map, lint-scope brand mentions).

Canonical/template: fail. Consumer: warn (a consumer may rename its own headings).

Usage: check-cross-refs.py   (resolves the repo root from its own location)
"""
import os
import re
import sys

# A backticked section name asserted to live in AGENTS.md, in either order.
REF_RES = [
    re.compile(r"`([^`]+)`\s+in\s+AGENTS\.md"),
    re.compile(r"AGENTS\.md\s+`([^`]+)`"),
]


def _repo_root():
    cand = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return cand if os.path.isdir(os.path.join(cand, "agents")) else os.getcwd()


def headings_of(text):
    """Set of heading texts (## Foo -> 'Foo') in a markdown string."""
    return {m.strip() for m in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text)}


def scan_skill_refs(skills_dir):
    """List of (skill, section_name) each SKILL.md asserts lives in AGENTS.md."""
    refs = []
    for d in sorted(os.listdir(skills_dir)):
        p = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        for rx in REF_RES:
            for name in rx.findall(text):
                refs.append((d, name.strip()))
    return refs


def main():
    root = _repo_root()
    skills_dir = os.path.join(root, "agents/dev-skills")
    if not os.path.isdir(skills_dir):
        print(
            "FAIL: agents/dev-skills not found under %s — wrong location or broken "
            "install; refusing to pass vacuously." % root
        )
        return 1

    is_consumer = os.path.isfile(
        os.path.join(root, ".neyra-dev-kit.source")
    ) and not os.path.isfile(os.path.join(root, ".neyra-kit-canonical"))

    # Resolve against the governance the kit ships: the template in canon, the rendered
    # include in a consumer.
    template = os.path.join(root, "agents/neyra-dev-kit/templates/AGENTS.include.md.tmpl")
    installed = os.path.join(root, "AGENTS.neyra-devkit.md")
    target = template if os.path.isfile(template) else (installed if os.path.isfile(installed) else None)
    if target is None:
        print("note: no AGENTS governance doc found (template or installed) — skip cross-ref check")
        return 0

    with open(target, encoding="utf-8") as fh:
        headings = headings_of(fh.read())
    problems = [(d, name) for (d, name) in scan_skill_refs(skills_dir) if name not in headings]

    rel = os.path.relpath(target, root)
    if problems:
        label = "WARN" if is_consumer else "FAIL"
        mark = "!" if is_consumer else "x"
        print("%s dead AGENTS.md section anchor(s) — not a heading in %s:" % (label, rel))
        for d, name in problems:
            print("   %s agents/dev-skills/%s/SKILL.md -> `%s`" % (mark, d, name))
        return 0 if is_consumer else 1

    mode = " [consumer: warn-only]" if is_consumer else ""
    print("ok: all dev-skill AGENTS.md section refs resolve in %s%s" % (rel, mode))
    return 0


if __name__ == "__main__":
    sys.exit(main())
