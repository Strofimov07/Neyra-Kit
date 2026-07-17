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

# Bundled design skills: agents/design-skills/<id>/ (kit-authored source) → .claude/skills/<id>/.
# These are the kit's portable auto-inject Skills (frontend/design craft). Synced FIRST so a
# same-named project skill (settings/skills/, below) overrides it — loader contract: project > bundled.
# Best-effort — must NEVER block session start (all failures swallowed).
if [ -n "$ROOT" ] && [ -d "$ROOT/agents/design-skills" ]; then
  for d in "$ROOT/agents/design-skills"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    dest="$ROOT/.claude/skills/$(basename "$d")"
    mkdir -p "$dest" 2>/dev/null || continue
    if command -v rsync >/dev/null 2>&1; then rsync -a --delete "$d" "$dest/" 2>/dev/null || true
    else cp -R "${d}." "$dest/" 2>/dev/null || true; fi
  done
fi

# Project skills auto-surface: settings/skills/<id>/ (tracked source) → .claude/skills/<id>/
# (generated, gitignored). install.sh does the full sync; this keeps it fresh every session so
# a skill dropped into settings/skills/ shows up next start without a manual re-install.
# Best-effort — must NEVER block session start (all failures swallowed).
if [ -n "$ROOT" ] && [ -d "$ROOT/settings/skills" ]; then
  for d in "$ROOT/settings/skills"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    dest="$ROOT/.claude/skills/$(basename "$d")"
    mkdir -p "$dest" 2>/dev/null || continue
    if command -v rsync >/dev/null 2>&1; then rsync -a --delete "$d" "$dest/" 2>/dev/null || true
    else cp -R "${d}." "$dest/" 2>/dev/null || true; fi
  done
fi

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
