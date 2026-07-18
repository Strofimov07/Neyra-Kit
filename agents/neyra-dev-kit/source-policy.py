#!/usr/bin/env python3
"""Identify the single repository allowed to author shared Neyra-Kit changes."""

import argparse
import subprocess
import sys
from pathlib import Path


CANONICAL_REMOTE = "git@github.com:Strofimov07/Neyra-Kit.git"
CANONICAL_ID = "github.com/strofimov07/neyra-kit"
MARKER = ".neyra-kit-canonical"
SOURCE_STAMP = ".neyra-dev-kit.source"


def normalize_remote(value: str) -> str:
    remote = value.strip().removesuffix(".git")
    if remote.startswith("git@github.com:"):
        remote = "github.com/" + remote.removeprefix("git@github.com:")
    elif remote.startswith("https://github.com/"):
        remote = remote.removeprefix("https://")
    elif remote.startswith("ssh://git@github.com/"):
        remote = "github.com/" + remote.removeprefix("ssh://git@github.com/")
    return remote.lower()


def origin(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def classify(root: Path) -> tuple[str, str]:
    marker = root / MARKER
    remote = origin(root)
    if marker.is_file():
        expected = f"repository={CANONICAL_REMOTE}"
        if marker.read_text(encoding="utf-8").strip() != expected:
            return "invalid", f"{MARKER} must contain exactly {expected!r}"
        if normalize_remote(remote) != CANONICAL_ID:
            return "invalid", f"canonical marker exists but origin is {remote or 'missing'}"
        return "canonical", f"canonical authoring source: {CANONICAL_REMOTE}"

    stamp = root / SOURCE_STAMP
    if stamp.is_file() and CANONICAL_REMOTE in stamp.read_text(encoding="utf-8"):
        return "consumer", f"consumer install; canonical source: {CANONICAL_REMOTE}"
    return "consumer", f"consumer or unstamped checkout; canonical source: {CANONICAL_REMOTE}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--require-canonical", action="store_true")
    args = parser.parse_args(argv)

    mode, detail = classify(args.root.resolve())
    if mode == "invalid":
        print(f"source policy invalid: {detail}", file=sys.stderr)
        return 2
    if args.require_canonical and mode != "canonical":
        print(
            f"source policy blocked: {detail}; do not author shared kit changes in a consumer",
            file=sys.stderr,
        )
        return 2
    print(f"{mode}: {detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
