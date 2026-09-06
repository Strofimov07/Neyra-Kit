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
. "$DIR/lib/host-io.sh" 2>/dev/null || exit 0
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

# Skill ↔ subagent rows that differ from the skill name in THIS install (NEB-2279 §1): a
# consumer agent diffed the skills catalog against .claude/agents/, counted nine "missing"
# subagents and dispatched `contract-safety` — whose subagent is called contract-checker.
# The mapping table knew; nothing showed it at the moment of dispatch. Best-effort.
if [ -n "$ROOT" ] && [ -f "$DIR/../check-skill-mapping.py" ]; then
  status="$(cd "$ROOT" && python3 "$DIR/../check-skill-mapping.py" --agents-status 2>/dev/null || true)"
  [ -n "$status" ] && CTX="$CTX

$status"
fi

# Handoff + tracker-outage debt (NEB-1669). A session that ended with open work, or ran
# through a dead tracker, leaves `.neyra/handoff.md` and a mutation queue behind; the next
# session must see both before doing anything else — a fallback nobody is reminded of is
# not a fallback (the prose one the bootstrap named did not even exist on disk in TF).
if [ -n "$ROOT" ]; then
  if [ -s "$ROOT/.neyra/handoff.md" ]; then
    CTX="$CTX

## Handoff from the previous session (.neyra/handoff.md)
Act on \"Pending tracker mutations\" first, then continue from \"In progress\". Overwrite the file as state changes; delete it when nothing is open.

$(head -c 6000 "$ROOT/.neyra/handoff.md" 2>/dev/null)"
  fi
  debt="$(cd "$ROOT" && python3 "$DIR/../tracker-queue.py" status 2>/dev/null || true)"
  pend="$ROOT/.neyra/kit-evolution-pending.log"
  if [ -s "$pend" ]; then
    n="$(grep -c . "$pend" 2>/dev/null || echo 0)"
    mt="$(stat -f %m "$pend" 2>/dev/null || stat -c %Y "$pend" 2>/dev/null || date +%s)"
    age="$(( ( $(date +%s) - mt ) / 86400 ))"
    debt="$debt
$n pending kit-evolution signal(s) in .neyra/kit-evolution-pending.log (last written ${age}d ago) — file them in the Neyra Skills Kit Linear project now, then clear the file."
  fi
  if [ -n "$(printf '%s' "$debt" | tr -d '[:space:]')" ]; then
    CTX="$CTX

## Tracker debt — replay before new work
$debt"
  fi
fi

nk_emit_context "$CTX" 2>/dev/null || exit 0
