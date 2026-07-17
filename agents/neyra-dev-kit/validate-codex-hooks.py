#!/usr/bin/env python3
"""Validate the Neyra hooks required by the current Codex hooks.json contract."""

import json
import pathlib
import sys


REQUIRED = {
    "SessionStart": ("session-start.sh", None),
    "PreToolUse": ("pre-tool-use-guard.sh", "Edit|Write"),
    "PostToolUse": ("post-tool-use-format.sh", "Edit|Write"),
    "Stop": ("stop-gate.sh", None),
}


def validate(path: pathlib.Path) -> list[str]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read valid JSON from {path}: {exc}"]

    hooks = config.get("hooks") if isinstance(config, dict) else None
    if not isinstance(hooks, dict):
        return ["current Codex hooks.json requires a top-level 'hooks' object"]

    errors = []
    for event, (script, expected_matcher) in REQUIRED.items():
        groups = hooks.get(event)
        if not isinstance(groups, list) or not groups:
            errors.append(f"missing non-empty hooks.{event} matcher-group list")
            continue

        found = False
        for group in groups:
            if not isinstance(group, dict):
                continue
            handlers = group.get("hooks")
            if not isinstance(handlers, list):
                continue
            for handler in handlers:
                if not isinstance(handler, dict) or script not in handler.get(
                    "command", ""
                ):
                    continue
                found = True
                if handler.get("type") != "command":
                    errors.append(f"{event} {script} handler must use type=command")
                command = handler.get("command", "")
                if "NEYRA_HOOK_HOST=codex" not in command:
                    errors.append(f"{event} {script} must set NEYRA_HOOK_HOST=codex")
                if "$(git rev-parse --show-toplevel)" not in command:
                    errors.append(f"{event} {script} must resolve from the Git root")
                if expected_matcher and group.get("matcher") != expected_matcher:
                    errors.append(
                        f"{event} {script} matcher must be {expected_matcher!r}"
                    )
        if not found:
            errors.append(f"hooks.{event} does not register {script}")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {pathlib.Path(sys.argv[0]).name} <hooks.json>", file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1])
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"ok: Codex hooks config matches current schema ({path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
