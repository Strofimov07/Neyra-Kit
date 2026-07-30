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
. "$DIR/lib/host-io.sh" 2>/dev/null || exit 0
nk_load

have() { command -v "$1" >/dev/null 2>&1; }
ROOT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$DIR/../../.." && pwd)}"
# Format only when the repo actually adopted the formatter — i.e. a config file is present.
# Without this the hook imposes the tool's DEFAULT style on a repo that never opted in
# (measured: 79/146 tracked .py rewritten from a one-line edit in a repo with ruff but no
# config). has_cfg globs the repo root (NEB-1650 #1).
has_cfg() { local f; for f in "$@"; do compgen -G "$ROOT_DIR/$f" >/dev/null 2>&1 && return 0; done; return 1; }
while IFS= read -r path; do
  { [ -z "$path" ] || [ ! -f "$path" ]; } && continue
  # Only touch files inside this repo — an absolute path from the caller could point
  # anywhere (NEB-1650 #2). A relative path is repo-local by construction.
  case "$path" in "$ROOT_DIR"/*) : ;; /*) continue ;; esac
  case "$path" in
    *.py)                   have ruff && has_cfg pyproject.toml ruff.toml .ruff.toml setup.cfg && ruff format "$path" >/dev/null 2>&1 || true ;;
    *.swift)                have swiftformat && has_cfg .swiftformat && swiftformat "$path" >/dev/null 2>&1 || true ;;
    *.ts|*.tsx|*.js|*.jsx)  have prettier && has_cfg .prettierrc .prettierrc.* prettier.config.* && prettier -w "$path" >/dev/null 2>&1 || true ;;
  esac
done < <(nk_edit_paths)
exit 0
