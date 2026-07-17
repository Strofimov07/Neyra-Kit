#!/usr/bin/env python3
"""Egress guard for bundled design skills.

The vendored Impeccable skill must not phone home. Upstream `context.mjs` fetches
`https://impeccable.style/api/version` (a version/update check) on command context
build; we neutralize it (`fetchLatestSkillVersion` -> `return null`). This guard fails
if that phone-home is reintroduced — e.g. after a naive re-copy of `context.mjs` from a
newer upstream without re-applying the patch.

Scope: intentionally targeted at the known vendor-egress pattern (not a general network
linter), so it has zero false positives on the skill's legitimate localhost traffic
(`live-*` preview server, `127.0.0.1` dev-port probing). Comments are stripped first, so
the commented-out upstream call and doc-link comments do not trip it.

Usage: check-egress.py [design-skills-dir]   (default: agents/design-skills)
Exit 0 = clean, 1 = phone-home present.
"""

import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "agents/design-skills"

# A network call whose target is the vendor update host / version endpoint.
BAD = re.compile(r"fetch\s*\([^)]*(UPDATE_HOST|api/version|impeccable\.style)", re.I)


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)  # /* block */
    src = re.sub(r"//[^\n]*", "", src)  # // line
    return src


def main() -> int:
    if not os.path.isdir(ROOT):
        print(f"egress guard: no {ROOT} — nothing to check")
        return 0
    hits = []
    for dirpath, _dirs, files in os.walk(ROOT):
        for f in files:
            if not f.endswith((".mjs", ".js")):
                continue
            p = os.path.join(dirpath, f)
            try:
                code = strip_comments(
                    open(p, encoding="utf-8", errors="replace").read()
                )
            except OSError:
                continue
            for m in BAD.finditer(code):
                hits.append((p, m.group(0)[:70].replace("\n", " ")))
    if hits:
        print("egress guard FAIL: a bundled skill would phone home to the vendor.")
        print("Re-apply the fetchLatestSkillVersion() -> `return null` patch")
        print("(see agents/design-skills/IMPECCABLE.md). Offending calls:")
        for p, snip in hits:
            print(f"   {p}: {snip} …")
        return 1
    print(f"egress guard OK: no vendor phone-home under {ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
