#!/usr/bin/env bash
# neyra-dev-kit publisher — sync the generic kit layers to the external repo
# (github.com/Strofimov07/Neyra-Kit). The monorepo is the canon; the external
# repo is a published artifact. One-way flow: monorepo → external.
#
# Usage:
#   publish.sh <path-to-neyra-kit-clone> [--dry-run]
#
# Gate: lint-scope.py must pass — a project fact (IP, workspace id, internal
# name) inside a generic layer FAILS the publish. This is the enforcement for
# the scoping rule in settings/README.md.
#
# Ships: agents/dev-skills/, agents/product-skills/, agents/mgmt-skills/,
# agents/design-skills/ (bundled auto-inject Skills, third-party MIT, license retained),
# agents/neyra-dev-kit/ (tooling + example configs only — real configs live
# in the consumer's settings/), .claude/agents/, README.md (rendered from
# templates/EXTERNAL_README.md — the external root README is canon-managed,
# do not hand-edit it there), and a settings/ skeleton (README + examples).
# Also prunes legacy paths superseded by renames. Commits with the kit
# VERSION; you push.
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO="$(cd "$KIT_DIR/../.." && pwd)"
VERSION="$(cat "$KIT_DIR/VERSION")"

EXT="${1:?usage: publish.sh <path-to-neyra-kit-clone> [--dry-run]}"
DRY=0; [[ "${2:-}" == "--dry-run" ]] && DRY=1

EXT="$(cd "$EXT" && pwd)"
git -C "$EXT" rev-parse --git-dir >/dev/null 2>&1 || { echo "error: $EXT is not a git repo" >&2; exit 1; }
remote_url="$(git -C "$EXT" remote get-url origin 2>/dev/null || true)"
[[ "$remote_url" == *"Neyra-Kit"* ]] || { echo "error: $EXT origin is '$remote_url', expected the Neyra-Kit repo — refusing to publish into the wrong clone" >&2; exit 1; }
[[ -z "$(git -C "$EXT" status --porcelain)" ]] || { echo "error: $EXT has uncommitted changes — commit or stash them first" >&2; exit 1; }

echo "publish neyra-dev-kit v$VERSION → $EXT"

echo "Gate — skill-mapping consumer regression tests:"
python3 "$KIT_DIR/test-check-skill-mapping.py" \
  || { echo "publish blocked: skill-mapping consumer regression test failed" >&2; exit 1; }

echo "Gate — portable reviewer regression tests:"
python3 "$KIT_DIR/test-portable-reviewers.py" \
  || { echo "publish blocked: portable reviewer regression test failed" >&2; exit 1; }

echo "Gate — Codex hooks contract regression tests:"
python3 "$KIT_DIR/test-codex-hooks.py" \
  || { echo "publish blocked: Codex hooks contract regression test failed" >&2; exit 1; }

echo "Gate — Impeccable live-server security regression tests:"
command -v node >/dev/null 2>&1 \
  || { echo "publish blocked: node is required for the bundled live-server security regression" >&2; exit 1; }
node --test "$MONOREPO/agents/design-skills/impeccable/scripts/live-server.security.test.mjs" \
  || { echo "publish blocked: bundled live-server security regression failed" >&2; exit 1; }

echo "Gate — lint-scope regression tests:"
python3 "$KIT_DIR/test-lint-scope.py" \
  || { echo "publish blocked: lint-scope regression test failed" >&2; exit 1; }

echo "Gate — lint-scope (generic layers must carry zero project facts):"
python3 "$KIT_DIR/lint-scope.py" "$MONOREPO/agents/dev-skills" "$MONOREPO/agents/product-skills" "$MONOREPO/agents/mgmt-skills" "$MONOREPO/agents/design-skills" \
  || { echo "publish blocked: fix the leaks (move facts to settings/, see settings/README.md)" >&2; exit 1; }

echo "Gate — no vendor phone-home in bundled skills:"
python3 "$KIT_DIR/check-egress.py" "$MONOREPO/agents/design-skills" \
  || { echo "publish blocked: a bundled skill would phone home — re-apply the patch (agents/design-skills/IMPECCABLE.md)" >&2; exit 1; }

run() { if [[ $DRY -eq 1 ]]; then echo "  [dry] $*"; else "$@"; fi; }

echo "Sync layers:"
run rsync -a --delete "$MONOREPO/agents/dev-skills/" "$EXT/agents/dev-skills/"
run rsync -a --delete "$MONOREPO/agents/product-skills/" "$EXT/agents/product-skills/"
run rsync -a --delete "$MONOREPO/agents/mgmt-skills/" "$EXT/agents/mgmt-skills/"
run rsync -a --delete "$MONOREPO/agents/design-skills/" "$EXT/agents/design-skills/"
# Kit tooling: exclude real per-repo configs (settings/ owns those in each
# consumer), bytecode, internal decision history / signal log, and internal
# research notes (spikes/).
run rsync -a --delete --exclude 'configs/*' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude 'decisionLog.md' --exclude 'signals.log' --exclude 'spikes/' --exclude 'lint-scope.local.txt' --exclude 'mcp-prefixes.local.txt' \
  "$MONOREPO/agents/neyra-dev-kit/" "$EXT/agents/neyra-dev-kit/"
# VERSION is the drift signal — force-copy it (macOS rsync 2.6.9 has 1-second
# mtime granularity: a same-size file rewritten within the same second is
# silently skipped, which shipped a stale stamp once).
run cp "$KIT_DIR/VERSION" "$EXT/agents/neyra-dev-kit/VERSION"
run cp "$KIT_DIR/VERSION" "$EXT/.neyra-dev-kit.version"
run mkdir -p "$EXT/agents/neyra-dev-kit/configs"
for ex in "$MONOREPO/agents/neyra-dev-kit/configs/"_*.example.sh; do
  [[ -f "$ex" ]] && run cp "$ex" "$EXT/agents/neyra-dev-kit/configs/"
done

# Subagents: allow-list only — the union of PORTABLE_AGENTS across manifests.
# Internal-only agents (modularity-guard, catalog-doc-syncer, incident-runbook,
# tier-4 wrappers not in any manifest) never ship; templated agents
# (linear-router, …) reach consumers via templates/ + install.sh render, not as
# Sergey's rendered copies. Per-user MCP instance ids are rewritten to
# {{LINEAR_MCP_PREFIX}} / {{NOTION_MCP_PREFIX}} placeholders on the way out —
# install.sh substitutes the consumer's own ids.
echo "Subagents (allow-list from manifests, MCP ids → placeholders):"
PORTABLE_ALL=()
for mf in "$KIT_DIR"/manifests/*.sh; do
  # shellcheck disable=SC1090
  PORTABLE_AGENTS=(); source "$mf"
  PORTABLE_ALL+=("${PORTABLE_AGENTS[@]}")
done
if [[ $DRY -eq 1 ]]; then
  echo "  [dry] ship $(printf '%s\n' "${PORTABLE_ALL[@]}" | sort -u | tr '\n' ' ')"
else
  rm -rf "${EXT:?}/.claude/agents"; mkdir -p "$EXT/.claude/agents"
  {
    echo "# Subagents (published set)"
    echo
    echo "Auto-invocable Claude Code wrappers around the kit's skills — the"
    echo "portable set from the kit manifests. Templated agents (linear-router,"
    echo "localization-checker, contract-checker) are rendered into your repo by"
    echo "install.sh from agents/neyra-dev-kit/templates/, not stored here."
    echo
    echo "| Subagent | Fires on |"
    echo "|---|---|"
  } > "$EXT/.claude/agents/README.md"
  for a in $(printf '%s\n' "${PORTABLE_ALL[@]}" | sort -u); do
    src="$MONOREPO/.claude/agents/$a.md"
    [[ -f "$src" ]] || { echo "  WARN: portable agent '$a' missing in canon — skipped"; continue; }
    # Hash→placeholder map lives in mcp-prefixes.local.txt (publish-excluded)
    # so this script, which ships externally, doesn't disclose the ids itself.
    if [[ -f "$KIT_DIR/mcp-prefixes.local.txt" ]]; then
      perl -pe "$(awk '!/^#/ && NF==2 {printf "s/%s/{{%s}}/g;", $1, $2}' "$KIT_DIR/mcp-prefixes.local.txt")" \
        "$src" > "$EXT/.claude/agents/$a.md"
    else
      cp "$src" "$EXT/.claude/agents/$a.md"
    fi
    desc="$(perl -ne 'if (/^description: (.*)/) { $d=$1; $d =~ s/\s*Use when.*$//i; print $d; exit }' "$src" | head -c 140)"
    echo "| [$a]($a.md) | $desc |" >> "$EXT/.claude/agents/README.md"
  done
  echo "  shipped $(printf '%s\n' "${PORTABLE_ALL[@]}" | sort -u | wc -l | tr -d ' ') agents + generated README"
fi

echo "Root README (RU+EN, canon: templates/EXTERNAL_README.*):"
run cp "$KIT_DIR/templates/EXTERNAL_README.en.md" "$EXT/README.md"
run cp "$KIT_DIR/templates/EXTERNAL_README.ru.md" "$EXT/README.ru.md"

echo "settings/ skeleton (examples only — consumer creates their own):"
run mkdir -p "$EXT/settings"
run cp "$KIT_DIR/templates/settings.README.external.md" "$EXT/settings/README.md"
run cp "$KIT_DIR/templates/settings.README.external.ru.md" "$EXT/settings/README.ru.md"
run cp "$KIT_DIR/templates/CONNECTORS.example.md" "$EXT/settings/CONNECTORS.example.md"

# Final leak check on the EXTERNAL tree itself — belt to lint-scope's
# braces: raw per-user MCP ids, Notion page ids, internal workspace slugs, or
# memory-bank references must not exist in the published artifact.
[[ $DRY -eq 1 ]] && { echo "(dry-run: nothing committed; leak check runs on real publish)"; exit 0; }

echo "External leak check (all file types, generic + local patterns):"
LEAK_ARGS=("$EXT")
if [[ -f "$KIT_DIR/lint-scope.local.txt" ]]; then
  LEAK_ARGS+=(--extra-patterns "$KIT_DIR/lint-scope.local.txt")
fi
python3 "$KIT_DIR/check-external-leaks.py" "${LEAK_ARGS[@]}" \
  || { echo "publish blocked: internal references in the external tree (above)" >&2; exit 1; }

# Prune paths superseded by renames — rsync --delete only cleans inside the
# dirs it syncs, not stale siblings left behind by a rename.
LEGACY_PATHS=( "agents/neyra-skills" "agents/neyra-dev-kit/spikes" )
for lp in "${LEGACY_PATHS[@]}"; do
  if [[ -e "$EXT/$lp" ]]; then run rm -rf "${EXT:?}/$lp"; echo "  pruned legacy $lp"; fi
done

if [[ $DRY -eq 1 ]]; then echo "(dry-run: nothing committed)"; exit 0; fi

ext_ver="$(cat "$EXT/agents/neyra-dev-kit/VERSION" 2>/dev/null || echo missing)"
[[ "$ext_ver" == "$VERSION" ]] || { echo "error: external VERSION '$ext_ver' != '$VERSION' after sync — investigate before committing" >&2; exit 1; }
ext_stamp="$(cat "$EXT/.neyra-dev-kit.version" 2>/dev/null || echo missing)"
[[ "$ext_stamp" == "$VERSION" ]] || { echo "error: external consumer stamp '$ext_stamp' != '$VERSION' after sync — investigate before committing" >&2; exit 1; }

if [[ -z "$(git -C "$EXT" status --porcelain)" ]]; then
  echo "external already up to date with v$VERSION — nothing to commit"
  exit 0
fi
git -C "$EXT" add -A   # safe here: publish clone is dedicated, tree verified clean above
git -C "$EXT" commit -m "Sync kit v$VERSION from monorepo"
echo "Committed v$VERSION in $EXT — review 'git -C $EXT show --stat HEAD', then push."
