#!/usr/bin/env bash
# neyra-dev-kit SessionStart hook.
#
# Force-injects the kit core (KIT_BOOTSTRAP.md) into the model's context at the
# start of every session, so the agent knows the kit exists and its gates are
# mandatory from turn one — instead of relying on the model deciding to read
# AGENTS.md. This is the Neyra analogue of superpowers' `using-superpowers`
# bootstrap, but it encodes our own rules (post-implementation gate, test-first,
# transparency, Linear hygiene).
#
# Hosts: Claude Code + Codex inject via SessionStart additionalContext (same
# schema); Cursor uses an always-apply rule instead, so this is a no-op there.
# Safety: on ANY error it emits nothing and exits 0 — a bootstrap hook must never
# block a session from starting.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib/host-io.sh"
CORE="$DIR/../KIT_BOOTSTRAP.md"
[ -f "$CORE" ] || exit 0

CTX="$(cat "$CORE")"

# Onboarding nudge — only in a consumer repo (version stamp present) whose
# settings/ scope is missing or still empty. Best-effort; never blocks.
ROOT="${CLAUDE_PROJECT_DIR:-}"
[ -z "$ROOT" ] && ROOT="$(cd "$DIR/../../.." 2>/dev/null && pwd)"
if [ -n "$ROOT" ] && [ -f "$ROOT/.neyra-dev-kit.version" ]; then
  if [ ! -f "$ROOT/settings/CONNECTORS.md" ] && [ ! -f "$ROOT/settings/README.md" ]; then
    CTX="$CTX

## ⚠ Kit installed but not onboarded
This repo has the kit but no filled-in \`settings/\` scope (configs, connectors,
facts, brand). Suggest running the \`kit-onboarding\` subagent now — a short
interview that fills everything the kit needs to work at full quality."
  fi
fi

nk_emit_context "$CTX" 2>/dev/null || exit 0
