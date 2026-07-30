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
        # AGENTS.md-section references are a dev-skill concern; a non-dev bundle
        # (mgmt/product/growth) ships no agents/dev-skills, so the check is N/A, not a
        # failure (NEB-1484). Fail closed only when NO skills layer exists at all.
        others = [
            d
            for d in ("agents/mgmt-skills", "agents/product-skills")
            if os.path.isdir(os.path.join(root, d))
        ]
        if others:
            print("note: no agents/dev-skills — non-dev bundle; cross-ref check N/A")
            return 0
        print(
            "FAIL: agents/dev-skills not found under %s — wrong location or broken "
            "install; refusing to pass vacuously." % root
        )
        return 1

    is_consumer = os.path.isfile(
        os.path.join(root, ".neyra-dev-kit.source")
    ) and not os.path.isfile(os.path.join(root, ".neyra-kit-canonical"))

    if is_consumer:
        # In a consumer the referenced sections live in the repo's own AGENTS.md / CLAUDE.md —
        # install.sh appends the kit block there, not into AGENTS.neyra-devkit.md (that render
        # is built from $GOVERNANCE_TMPL and carries no such sections by construction). A skill
        # that says "`X` in AGENTS.md" means AGENTS.md, so resolve against the union of all
        # three (NEB-1647). A consumer may rename its headings → warn, never fail.
        sources = [
            os.path.join(root, f)
            for f in ("AGENTS.md", "CLAUDE.md", "AGENTS.neyra-devkit.md")
            if os.path.isfile(os.path.join(root, f))
        ]
        if not sources:
            print("note: no AGENTS.md/CLAUDE.md/AGENTS.neyra-devkit.md — skip cross-ref check")
            return 0
        headings = set()
        for p in sources:
            with open(p, encoding="utf-8") as fh:
                headings |= headings_of(fh.read())
        target_label = ", ".join(os.path.basename(p) for p in sources)
    else:
        # Canonical: resolve against the shipped governance template; a dead anchor fails.
        template = os.path.join(root, "agents/neyra-dev-kit/templates/AGENTS.include.md.tmpl")
        installed = os.path.join(root, "AGENTS.neyra-devkit.md")
        target = template if os.path.isfile(template) else (installed if os.path.isfile(installed) else None)
        if target is None:
            print("note: no AGENTS governance doc found (template or installed) — skip cross-ref check")
            return 0
        with open(target, encoding="utf-8") as fh:
            headings = headings_of(fh.read())
        target_label = os.path.relpath(target, root)

    problems = [(d, name) for (d, name) in scan_skill_refs(skills_dir) if name not in headings]

    if problems:
        label = "WARN" if is_consumer else "FAIL"
        mark = "!" if is_consumer else "x"
        print("%s dead AGENTS.md section anchor(s) — not a heading in %s:" % (label, target_label))
        for d, name in problems:
            print("   %s agents/dev-skills/%s/SKILL.md -> `%s`" % (mark, d, name))
        return 0 if is_consumer else 1

    mode = " [consumer: warn-only]" if is_consumer else ""
    print("ok: all dev-skill AGENTS.md section refs resolve in %s%s" % (target_label, mode))
    return 0


if __name__ == "__main__":
    sys.exit(main())
