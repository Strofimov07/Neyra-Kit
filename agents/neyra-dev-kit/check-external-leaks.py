#!/usr/bin/env python3
"""Fail when a published kit tree contains project-specific references."""

import argparse
import ipaddress
import re
import sys
from pathlib import Path
from typing import Optional


IP_PATTERN = re.compile(r"(?<![\w.])\d{1,3}(?:\.\d{1,3}){3}\b")
STATIC_PATTERNS = [
    (re.compile(r"mcp__[0-9a-f]{8}-"), "MCP server-instance id"),
    (re.compile(r"notion\.so/[0-9a-f]{16}"), "Notion page id"),
    (re.compile(r"docs/memory-bank"), "legacy memory-bank path"),
    (re.compile(r"feedback_"), "internal memory slug"),
]
SELF_FILES = {Path(__file__).name, "test-external-leaks.py"}


def load_extra_patterns(path: Optional[Path]) -> list[tuple[re.Pattern, str]]:
    if path is None or not path.is_file():
        return []
    patterns = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append((re.compile(line, re.I), "internal name (local list)"))
    return patterns


def scan(root: Path, extra_patterns: Optional[Path] = None) -> list[str]:
    findings = []
    patterns = STATIC_PATTERNS + load_extra_patterns(extra_patterns)
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or ".git" in file_path.parts or file_path.name in SELF_FILES:
            continue
        raw = file_path.read_bytes()
        if b"\0" in raw:
            continue
        for lineno, line in enumerate(raw.decode("utf-8", errors="ignore").splitlines(), 1):
            for match in IP_PATTERN.finditer(line):
                try:
                    is_loopback = ipaddress.ip_address(match.group(0)).is_loopback
                except ValueError:
                    is_loopback = False
                if not is_loopback:
                    findings.append(f"{file_path}:{lineno}: IP address: {line.strip()[:100]}")
                    break
            for pattern, label in patterns:
                if pattern.search(line):
                    findings.append(f"{file_path}:{lineno}: {label}: {line.strip()[:100]}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--extra-patterns", type=Path)
    args = parser.parse_args()

    findings = scan(args.root, args.extra_patterns)
    if findings:
        for finding in findings[:10]:
            print(finding)
        print(f"external leak check: {len(findings)} finding(s)")
        return 1
    print("external leak check: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
