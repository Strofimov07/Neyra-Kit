#!/usr/bin/env bash
# neyra-dev-kit PreToolUse guard.
#
# Blocks Edit/Write to clearly generated or kit-rendered files (which must be
# regenerated, not hand-edited). Default ALLOW: only an explicit denylist match
# blocks. The host shim turns a match into the right block signal per tool
# (Claude/Codex: exit 2 + stderr; Cursor: {"permission":"deny"}). Safe on any
# parse error (allow), so the guard can never wedge a session.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib/host-io.sh"
nk_load

path="$(nk_edit_path)"
[ -z "$path" ] && exit 0

block_managed_path() {
  nk_metric guard_block path "$path"
  nk_block_edit "neyra-dev-kit: '$path' is generated / kit-managed — regenerate it (re-run install.sh or the generator), do not hand-edit."
}

case "$path" in
  generated/*|*/generated/*|*.generated.*|*_pb2.py)
    block_managed_path ;;
  AGENTS.neyra-devkit.md|*/AGENTS.neyra-devkit.md|.neyra-dev-kit.version|*/.neyra-dev-kit.version)
    block_managed_path ;;
esac
exit 0
