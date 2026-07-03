#!/usr/bin/env bash
# neyra-dev-kit PostToolUse formatter.
#
# Formats the just-edited CODE file with the project's formatter if it is
# installed; silent no-op otherwise. Never blocks (always exit 0). Markdown is
# intentionally excluded to avoid reformat races with in-flight multi-edit work.
# Path resolution is host-aware via the shim (Claude/Codex PostToolUse, Cursor
# afterFileEdit).
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib/host-io.sh"
nk_load

path="$(nk_edit_path)"
{ [ -z "$path" ] || [ ! -f "$path" ]; } && exit 0

have() { command -v "$1" >/dev/null 2>&1; }
case "$path" in
  *.py)                   have ruff && ruff format "$path" >/dev/null 2>&1 || true ;;
  *.swift)                have swiftformat && swiftformat "$path" >/dev/null 2>&1 || true ;;
  *.ts|*.tsx|*.js|*.jsx)  have prettier && prettier -w "$path" >/dev/null 2>&1 || true ;;
esac
exit 0
