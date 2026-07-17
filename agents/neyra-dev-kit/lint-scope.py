#!/usr/bin/env python3
"""Scope linter: generic kit layers must contain zero project facts.

Scans agents/dev-skills/, agents/product-skills/, and agents/mgmt-skills/ (the layers published to the
external Neyra-Kit repo) for project-specific facts that belong in settings/:
IP addresses, MCP server-instance hashes, Notion page hashes, and known internal
server/db names. Errors fail the run (pre-commit + publish gate). Brand-name
mentions are warnings only — legitimate as *examples*, but worth an eyeball.

Usage: lint-scope.py [dir ...]   (default: agents/dev-skills agents/product-skills agents/mgmt-skills)
"""

import ipaddress
import re
import sys
from pathlib import Path

# Hard facts — never legitimate inside a generic skill. ERROR.
# IP pattern: lookbehind excludes "v1.2.3.4"-style version tags (letter/dot glued
# to the first octet) without ever suppressing a bare 4-octet address.
ERROR_PATTERNS = [
    (
        re.compile(r"(?<![\w.])\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
        "IP address",
    ),
    (re.compile(r"mcp__[0-9a-f]{8}-[0-9a-f]{4}"), "MCP server-instance id"),
    (re.compile(r"notion\.so/[0-9a-f]{16,}"), "Notion page id"),
    (re.compile(r"linear\.app/[\w-]+/"), "Linear workspace URL"),
]

# Internal-name patterns load from lint-scope.local.txt (publish-excluded) so
# the shipped linter doesn't itself disclose the names it guards. Missing
# file → generic patterns above still apply.
_local = Path(__file__).parent / "lint-scope.local.txt"
if _local.is_file():
    for _line in _local.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#"):
            ERROR_PATTERNS.append((re.compile(_line, re.I), "internal name (local list)"))

# Brand names — allowed as examples, but flag for review. WARNING.
# Deliberately case-sensitive: capitalized = prose/brand usage worth an eyeball;
# lowercase (paths like agents/neyra-dev-kit/) is identifier plumbing, not copy.
WARN_PATTERN = re.compile(r"\b(Neyra|Nebula|Lumen)\b")


def is_allowed_match(label: str, value: str) -> bool:
    if label != "IP address":
        return False
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def lint(dirs: list[str]) -> int:
    errors, warnings = [], []
    for d in dirs:
        root = Path(d)
        if not root.is_dir():
            print(f"lint-scope: skip missing dir {d}")
            continue
        for f in sorted(root.rglob("*.md")):
            for lineno, line in enumerate(
                f.read_text(encoding="utf-8").splitlines(), 1
            ):
                for pat, label in ERROR_PATTERNS:
                    if any(
                        not is_allowed_match(label, match.group(0))
                        for match in pat.finditer(line)
                    ):
                        errors.append(f"{f}:{lineno}: {label}: {line.strip()[:100]}")
                if WARN_PATTERN.search(line):
                    warnings.append(
                        f"{f}:{lineno}: brand mention: {line.strip()[:100]}"
                    )
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(
            f"\nlint-scope: {len(errors)} error(s) — project facts belong in settings/ "
            "(see settings/README.md), reach skills via {{PLACEHOLDER}} or a facts-file pointer."
        )
        return 1
    print(f"lint-scope: OK ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(lint(sys.argv[1:] or ["agents/dev-skills", "agents/product-skills", "agents/mgmt-skills"]))
