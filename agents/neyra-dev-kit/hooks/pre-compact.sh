#!/usr/bin/env bash
# neyra-dev-kit PreCompact hook (NEB-1669).
#
# Compaction summarizes the context; what was open, decided, and queued survives only if
# it is on disk. Two jobs, both best-effort — never blocks, always exit 0:
#  1. Stamp `.neyra/handoff.md` with a compaction marker, creating the skeleton when it is
#     absent, so the post-compaction turn finds a structured place to write what it still
#     knows — and a later reader can tell "above this line was in context, below it was
#     written after the summary".
#  2. Record the event in kit telemetry (`compact trigger manual|auto`).
# Host: Claude Code PreCompact (stdin carries `trigger`). Codex and Cursor expose no
# compaction event; there the handoff file is written by the protocol alone (KIT_BOOTSTRAP).
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib/host-io.sh" 2>/dev/null || exit 0
nk_load

ROOT="${CLAUDE_PROJECT_DIR:-}"
[ -z "$ROOT" ] && ROOT="$(cd "$DIR/../../.." 2>/dev/null && pwd)"
[ -n "$ROOT" ] || exit 0
mkdir -p "$ROOT/.neyra" 2>/dev/null || exit 0
H="$ROOT/.neyra/handoff.md"
trigger="$(nk_json trigger)"; [ -z "$trigger" ] && trigger="unknown"

if [ ! -f "$H" ]; then
  cat > "$H" <<'TMPL'
# Handoff — written for the next session (local, never committed)

Overwrite each section with the current truth; delete this file when nothing is open.
The next session receives it at start and acts on "Pending tracker mutations" first.

## Completed this session
-

## In progress (exact next step)
-

## Blockers
-

## Decisions made (and why)
-

## Context to load first
-

## Pending tracker mutations
Queue them with `python3 agents/neyra-dev-kit/tracker-queue.py add …`; see `list`.
TMPL
fi
printf '\n---\n**[compaction (%s) at %s]** — everything above this line was in context before the summary; what was decided after it must be re-stated below.\n' \
  "$trigger" "$(date -u +%Y-%m-%dT%H:%MZ)" >> "$H" 2>/dev/null || true
nk_metric compact trigger "$trigger"
exit 0
