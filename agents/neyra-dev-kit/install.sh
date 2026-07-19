#!/usr/bin/env bash
# neyra-dev-kit installer — roll a named skill kit into a repo.
#
# Usage:
#   install.sh [--dry-run|--doctor] [--allow-non-git] <kit> <target-repo-path> <config.sh>
#   install.sh [--dry-run|--doctor] [--allow-non-git] <target-repo-path> <config.sh>
#     (2-positional back-compat form: kit defaults to "dev")
#
# Sources manifests/<kit>.sh for the kit definition, then copies Layer A
# (portable skills + generic subagents) verbatim from the canonical Neyra-Kit repo,
# renders Layer B (templated subagents + AGENTS fragment) from <config.sh>,
# and writes a version stamp. Idempotent: overwrites only kit-managed files.
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$KIT_DIR/../.." && pwd)"
CANON_AGENTS="$SOURCE_ROOT/.claude/agents"
VERSION="$(cat "$KIT_DIR/VERSION")"
CANONICAL_REMOTE="git@github.com:Strofimov07/Neyra-Kit.git"
SOURCE_REVISION="$(git -C "$SOURCE_ROOT" rev-parse HEAD 2>/dev/null || printf 'unknown')"

python3 "$KIT_DIR/source-policy.py" --root "$SOURCE_ROOT" --require-canonical >/dev/null \
  || { echo "error: install.sh must run from the canonical Neyra-Kit clone" >&2; exit 2; }

DRY=0; ALLOW_NON_GIT=0; DOCTOR=0
while [[ "${1:-}" == --* ]]; do
  case "$1" in
    --dry-run) DRY=1;;
    --allow-non-git) ALLOW_NON_GIT=1;;
    --doctor) DOCTOR=1;;
    *) echo "unknown flag: $1" >&2; exit 1;;
  esac; shift
done

# Back-compat: 2-positional form (no kit) → default kit = dev.
if [[ $# -eq 2 ]]; then
  KIT="dev"
  TARGET="${1:?usage: install.sh [flags] [<kit>] <target-repo> <config.sh>}"
  CONFIG="${2:?usage: install.sh [flags] [<kit>] <target-repo> <config.sh>}"
else
  KIT="${1:?usage: install.sh [flags] [<kit>] <target-repo> <config.sh>}"
  TARGET="${2:?usage: install.sh [flags] [<kit>] <target-repo> <config.sh>}"
  CONFIG="${3:?usage: install.sh [flags] [<kit>] <target-repo> <config.sh>}"
fi

# Load manifest.
MANIFEST="$KIT_DIR/manifests/$KIT.sh"
[[ -f "$MANIFEST" ]] || { echo "error: unknown kit '$KIT' — no manifest at $MANIFEST" >&2; exit 1; }
# shellcheck disable=SC1090
source "$MANIFEST"

TARGET="$(cd "$TARGET" && pwd)"
if [[ $ALLOW_NON_GIT -eq 0 && $DOCTOR -eq 0 ]]; then
  git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 || { echo "error: $TARGET is not a git repo — pass --allow-non-git to override" >&2; exit 1; }
fi
[[ -f "$CONFIG" ]] || { echo "config not found: $CONFIG" >&2; exit 1; }

# Defaults; overridden by config.
ENABLE_LINEAR_ROUTER=1; ENABLE_LOCALIZATION_CHECKER=1; ENABLE_CONTRACT_CHECKER=1
ENABLE_NEYRA_MCP=0; ENABLE_FIREBASE_MCP=0; ENABLE_CURSOR_SKILLS=1; ENABLE_HOOKS=1
REPO_NAME=""; STACK=""; BUILD_VERIFY_CMD=""; LOCALES=""; I18N_MECHANISM=""
CONTRACT_STACK=""; LINEAR_WORKSPACE=""; LINEAR_ROUTING=""
# Linear MCP server-instance prefix the linear-router's tools resolve against. This is
# per-user/per-connection — a friend MUST set their own (find it via Claude Code /mcp).
# Empty → linear-router is skipped (never installed broken).
LINEAR_MCP_PREFIX=""
# Notion MCP instance id for portable agents that use Notion tools (same per-user
# semantics as LINEAR_MCP_PREFIX). Empty -> {{NOTION_MCP_PREFIX}} placeholders stay
# inert (those tools inactive), everything else works.
NOTION_MCP_PREFIX=""
FIGMA_MCP_PREFIX=""
# Optional project-scoped Neyra MCP entrypoint. Consumer config must provide it;
# the standalone canonical kit has no product runtime dependency.
NEYRA_MCP_ENTRY=""
FIREBASE_PROJECT_DIR=""
FIREBASE_MCP_TOOLS="firebase_read_resources,remoteconfig_get_template,remoteconfig_update_template,crashlytics_get_issue,crashlytics_list_events,crashlytics_batch_get_events,crashlytics_list_notes,crashlytics_get_report"
# NOTE: the config is executed as shell (sourced) — only run with configs you have reviewed.
# shellcheck disable=SC1090
source "$CONFIG"

FIREBASE_MCP_DIR=""
if [[ -n "$FIREBASE_PROJECT_DIR" ]]; then
  case "$FIREBASE_PROJECT_DIR" in
    /*) FIREBASE_MCP_DIR="$FIREBASE_PROJECT_DIR" ;;
    *) FIREBASE_MCP_DIR="$TARGET/$FIREBASE_PROJECT_DIR" ;;
  esac
fi

say()  { printf '  %s\n' "$*"; }
do_()  { if [[ $DRY -eq 1 ]]; then say "[dry] $*"; else eval "$*"; fi; }

render() { # render <template-file> -> stdout. Values passed via env (no code injection),
           # perl substitution so '&' and other regex-special chars in values are literal.
  REPO_NAME="$REPO_NAME" STACK="$STACK" BUILD_VERIFY_CMD="$BUILD_VERIFY_CMD" \
  LOCALES="$LOCALES" I18N_MECHANISM="$I18N_MECHANISM" CONTRACT_STACK="$CONTRACT_STACK" \
  LINEAR_WORKSPACE="$LINEAR_WORKSPACE" LINEAR_ROUTING="$LINEAR_ROUTING" NEYRA_MCP_ENTRY="$NEYRA_MCP_ENTRY" \
  LINEAR_MCP_PREFIX="$LINEAR_MCP_PREFIX" FIREBASE_MCP_DIR="$FIREBASE_MCP_DIR" \
  FIREBASE_MCP_TOOLS="$FIREBASE_MCP_TOOLS" \
  perl -0777 -pe '
    for my $k (qw(REPO_NAME STACK BUILD_VERIFY_CMD LOCALES I18N_MECHANISM CONTRACT_STACK LINEAR_WORKSPACE LINEAR_ROUTING NEYRA_MCP_ENTRY LINEAR_MCP_PREFIX FIREBASE_MCP_DIR FIREBASE_MCP_TOOLS)) {
      my $v = $ENV{$k} // ""; s/\{\{\Q$k\E\}\}/$v/g;
    }
  ' "$1"
}
write() { # write <dest> <<<content (stdin)
  if [[ $DRY -eq 1 ]]; then say "[dry] write $1"; cat > /dev/null; else mkdir -p "$(dirname "$1")"; cat > "$1"; fi
}

# Convert templated-agent id to its enable-flag name (e.g. linear-router → ENABLE_LINEAR_ROUTER).
# Uses tr (not bash-4 ${^^}) so it runs on stock macOS bash 3.2 too.
enable_flag() { echo "ENABLE_$(printf '%s' "$1" | tr 'a-z-' 'A-Z_')"; }

if [[ $DOCTOR -eq 1 ]]; then
  echo "neyra-dev-kit doctor v$VERSION — kit=$KIT_NAME — ${REPO_NAME:-?}"
  echo "  Zero-setup subagents (Read/Grep/Glob/Bash only — work for anyone, no accounts):"
  echo "    ${PORTABLE_AGENTS[*]} ${TEMPLATED_AGENTS[*]}"
  echo "  Needs external setup:"
  if [[ "$ENABLE_LINEAR_ROUTER" == "1" && -n "$LINEAR_MCP_PREFIX" ]]; then echo "    linear-router → Linear MCP (prefix set: $LINEAR_MCP_PREFIX)"
  elif [[ "$ENABLE_LINEAR_ROUTER" == "1" ]]; then echo "    linear-router → NEEDS your Linear MCP id in LINEAR_MCP_PREFIX (Claude Code: /mcp) — else skipped"
  else echo "    linear-router → disabled in config"; fi
  for srv in "${MCP_SERVERS[@]}"; do
    if [[ "$srv" == "neyra" ]]; then
      if [[ "$ENABLE_NEYRA_MCP" == "1" ]]; then echo "    neyra MCP (.mcp.json) → needs NEYRA_API_URL / NEYRA_API_KEY in your env"
      else echo "    neyra MCP → disabled in config"; fi
    elif [[ "$srv" == "firebase" ]]; then
      if [[ "$ENABLE_FIREBASE_MCP" == "1" ]]; then
        echo "    firebase MCP → npx + Firebase CLI auth; run: firebase login (or configure ADC)"
        echo "      project dir: ${FIREBASE_MCP_DIR:-NEEDS FIREBASE_PROJECT_DIR}; tools: $FIREBASE_MCP_TOOLS"
        echo "      IAM read: roles/cloudconfig.viewer; write: roles/cloudconfig.admin"
        echo "      Codex: codex mcp add firebase -- npx -y firebase-tools@latest mcp --dir \"$FIREBASE_MCP_DIR\" --tools \"$FIREBASE_MCP_TOOLS\""
      else echo "    firebase MCP → disabled in config"; fi
    fi
  done
  echo "  Notion: not required by the kit."
  exit 0
fi

echo "neyra-dev-kit v$VERSION [kit=$KIT_NAME] → $TARGET  (repo: ${REPO_NAME:-?})"
[[ $DRY -eq 1 ]] && echo "(dry-run: no files written)"

# Resolve the canonical skills source for this kit.
CANON_SKILLS="$SOURCE_ROOT/$SKILLS_SRC"
[[ -d "$CANON_SKILLS" ]] || { echo "error: SKILLS_SRC '$SKILLS_SRC' not found in canonical source at $CANON_SKILLS" >&2; exit 1; }

echo "Layer A — portable skills ($SKILLS_SRC):"
do_ "mkdir -p '$TARGET/$SKILLS_SRC'"
if [[ "${SKILLS[0]}" == "ALL" ]]; then
  # Copy the whole dir.
  if command -v rsync >/dev/null 2>&1; then
    do_ "rsync -a --delete '$CANON_SKILLS/' '$TARGET/$SKILLS_SRC/'"
  else
    do_ "cp -R '$CANON_SKILLS/'* '$TARGET/$SKILLS_SRC/'"
  fi
  SKILL_COUNT="$(find "$CANON_SKILLS" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')"
  say "synced $SKILL_COUNT skill dirs"
else
  # Copy only listed skill-id dirs.
  n=0
  for skill_id in "${SKILLS[@]}"; do
    src="$CANON_SKILLS/$skill_id"
    if [[ -d "$src" ]]; then
      if command -v rsync >/dev/null 2>&1; then
        do_ "rsync -a --delete '$src/' '$TARGET/$SKILLS_SRC/$skill_id/'"
      else
        do_ "cp -R '$src' '$TARGET/$SKILLS_SRC/'"
      fi
      n=$((n+1))
    else
      say "WARN: skill '$skill_id' not found in $CANON_SKILLS — skipped"
    fi
  done
  say "synced $n skill dirs"
fi

# Bundled design skills (kit-authored auto-inject Skills): $BUNDLED_SKILLS_SRC/<id>/ → .claude/skills/<id>/.
# Manifest opt-in (BUNDLED_SKILLS_SRC, set only by kits that ship them). The canonical dir is also
# copied into the target's portable layer so the consumer's session-start hook can re-sync it.
# Synced BEFORE project skills below so a same-named settings/skills/ entry overrides it (project > bundled).
if [[ -n "${BUNDLED_SKILLS_SRC:-}" && -d "$SOURCE_ROOT/$BUNDLED_SKILLS_SRC" ]]; then
  echo "Bundled skills — $BUNDLED_SKILLS_SRC → .claude/skills/:"
  CANON_BUNDLED="$SOURCE_ROOT/$BUNDLED_SKILLS_SRC"
  do_ "mkdir -p '$TARGET/$BUNDLED_SKILLS_SRC' '$TARGET/.claude/skills'"
  if command -v rsync >/dev/null 2>&1; then
    do_ "rsync -a --delete '$CANON_BUNDLED/' '$TARGET/$BUNDLED_SKILLS_SRC/'"
  else
    do_ "cp -R '$CANON_BUNDLED/'* '$TARGET/$BUNDLED_SKILLS_SRC/'"
  fi
  bs=0
  for d in "$CANON_BUNDLED"/*/; do
    [[ -f "${d}SKILL.md" ]] || continue
    sid="$(basename "$d")"
    # sid becomes a path component AND (via do_ → eval) part of a shell command. Kit-authored,
    # but sanitize anyway — same fail-closed guard as project skills. Reject anything but a plain id.
    if [[ ! "$sid" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
      say "WARN: skipping bundled skill dir with unsafe name: $sid"
      continue
    fi
    if command -v rsync >/dev/null 2>&1; then
      do_ "rsync -a --delete '$d' '$TARGET/.claude/skills/$sid/'"
    else
      do_ "mkdir -p '$TARGET/.claude/skills/$sid' && cp -R '${d}.' '$TARGET/.claude/skills/$sid/'"
    fi
    bs=$((bs+1))
  done
  say "synced $bs bundled skill(s) → .claude/skills/ (source: $BUNDLED_SKILLS_SRC; .claude copy generated — never hand-edit)"
fi

# Project-owned skills: settings/skills/<id>/ (tracked, kit never authors) → .claude/skills/<id>/
# (generated, gitignored). Same rsync --delete idiom as canon skills above; source of truth
# stays in settings/skills/, the .claude copy is regenerated each run — never hand-edited.
echo "Project skills — settings/skills/ → .claude/skills/ (repo-owned):"
PROJ_SKILLS="$TARGET/settings/skills"
if [[ -d "$PROJ_SKILLS" ]]; then
  do_ "mkdir -p '$TARGET/.claude/skills'"
  ps=0
  for d in "$PROJ_SKILLS"/*/; do
    [[ -f "${d}SKILL.md" ]] || continue
    sid="$(basename "$d")"
    # settings/skills/<id>/ is repo-checked-in and may come from a less-trusted PR.
    # sid becomes a path component AND (via do_ → eval below) part of a shell command,
    # so a crafted dir name like  a'$(touch pwned)b  would break out and execute.
    # Reject anything but a plain skill id — fail closed, skip the offender.
    if [[ ! "$sid" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
      say "WARN: skipping project skill dir with unsafe name: $sid"
      continue
    fi
    if command -v rsync >/dev/null 2>&1; then
      do_ "rsync -a --delete '$d' '$TARGET/.claude/skills/$sid/'"
    else
      do_ "mkdir -p '$TARGET/.claude/skills/$sid' && cp -R '${d}.' '$TARGET/.claude/skills/$sid/'"
    fi
    ps=$((ps+1))
  done
  say "synced $ps project skill(s) → .claude/skills/ (source in settings/skills/; .claude copy is generated — never hand-edit)"
else
  say "no settings/skills/ — nothing to sync (add settings/skills/<id>/SKILL.md for a project-owned skill)"
fi

echo "Layer A — portable subagents:"
do_ "mkdir -p '$TARGET/.claude/agents'"
for a in "${PORTABLE_AGENTS[@]}"; do
  if [[ -f "$CANON_AGENTS/$a.md" ]]; then
    do_ "cp '$CANON_AGENTS/$a.md' '$TARGET/.claude/agents/$a.md'"
    # Published copies carry {{LINEAR_MCP_PREFIX}}/{{NOTION_MCP_PREFIX}}
    # placeholders (MCP ids are per-user) — substitute the consumer's own ids.
    # No-op in the canonical clone (real ids, no placeholders) and in dry-run.
    if [[ $DRY -eq 0 ]]; then
      [[ -n "$LINEAR_MCP_PREFIX" ]] && perl -pi -e "s/\Q{{LINEAR_MCP_PREFIX}}\E/$LINEAR_MCP_PREFIX/g" "$TARGET/.claude/agents/$a.md"
      [[ -n "${NOTION_MCP_PREFIX:-}" ]] && perl -pi -e "s/\Q{{NOTION_MCP_PREFIX}}\E/$NOTION_MCP_PREFIX/g" "$TARGET/.claude/agents/$a.md"
      [[ -n "${FIGMA_MCP_PREFIX:-}" ]] && perl -pi -e "s/\Q{{FIGMA_MCP_PREFIX}}\E/$FIGMA_MCP_PREFIX/g" "$TARGET/.claude/agents/$a.md"
    fi
    say "$a"
  else say "WARN: $a.md not found in canon ($CANON_AGENTS) — skipped"; fi
done

if [[ "${CURSOR_SKILLS}" == "1" ]]; then
  echo "Cursor — symlink skills into .cursor/skills/:"
  do_ "mkdir -p '$TARGET/.cursor/skills'"
  n=0
  if [[ "${SKILLS[0]}" == "ALL" ]]; then
    for s in "$CANON_SKILLS"/*/; do
      id="$(basename "$s")"; [[ -f "$CANON_SKILLS/$id/SKILL.md" ]] || continue
      if [[ $DRY -eq 1 ]]; then say "[dry] link .cursor/skills/$id"; else ln -sfn "../../$SKILLS_SRC/$id" "$TARGET/.cursor/skills/$id"; fi
      n=$((n+1))
    done
  else
    for skill_id in "${SKILLS[@]}"; do
      [[ -f "$CANON_SKILLS/$skill_id/SKILL.md" ]] || continue
      if [[ $DRY -eq 1 ]]; then say "[dry] link .cursor/skills/$skill_id"; else ln -sfn "../../$SKILLS_SRC/$skill_id" "$TARGET/.cursor/skills/$skill_id"; fi
      n=$((n+1))
    done
  fi
  say "linked $n skills (.cursor/skills/<id> → ../../$SKILLS_SRC/<id>)"
fi

if [[ "${ENABLE_CODEX:-1}" == "1" ]]; then
  echo "Codex — symlink skills into .agents/skills/:"
  do_ "mkdir -p '$TARGET/.agents/skills'"
  n=0
  if [[ "${SKILLS[0]}" == "ALL" ]]; then
    for s in "$CANON_SKILLS"/*/; do
      id="$(basename "$s")"; [[ -f "$CANON_SKILLS/$id/SKILL.md" ]] || continue
      if [[ $DRY -eq 1 ]]; then say "[dry] link .agents/skills/$id"; else ln -sfn "../../$SKILLS_SRC/$id" "$TARGET/.agents/skills/$id"; fi
      n=$((n+1))
    done
  else
    for skill_id in "${SKILLS[@]}"; do
      [[ -f "$CANON_SKILLS/$skill_id/SKILL.md" ]] || continue
      if [[ $DRY -eq 1 ]]; then say "[dry] link .agents/skills/$skill_id"; else ln -sfn "../../$SKILLS_SRC/$skill_id" "$TARGET/.agents/skills/$skill_id"; fi
      n=$((n+1))
    done
  fi
  say "linked $n skills (.agents/skills/<id> → ../../$SKILLS_SRC/<id>) [Codex]"
fi

echo "Layer B — templated subagents:"
for tmpl_id in "${TEMPLATED_AGENTS[@]}"; do
  flag="$(enable_flag "$tmpl_id")"
  flag_val="${!flag:-1}"  # default enabled if not set in config
  tmpl_file="$KIT_DIR/templates/agents/$tmpl_id.md.tmpl"
  if [[ "$tmpl_id" == "linear-router" ]]; then
    if [[ "$ENABLE_LINEAR_ROUTER" == "1" && -n "$LINEAR_MCP_PREFIX" ]]; then
      render "$tmpl_file" | write "$TARGET/.claude/agents/linear-router.md"; say "linear-router (Linear MCP: $LINEAR_MCP_PREFIX)"
    elif [[ "$ENABLE_LINEAR_ROUTER" == "1" ]]; then
      say "linear-router SKIPPED — set LINEAR_MCP_PREFIX to your Linear MCP id (Claude Code: /mcp), then re-run"
    fi
  else
    if [[ "$flag_val" == "1" ]]; then
      if [[ -f "$tmpl_file" ]]; then
        render "$tmpl_file" | write "$TARGET/.claude/agents/$tmpl_id.md"; say "$tmpl_id"
      else
        say "WARN: template not found for $tmpl_id at $tmpl_file — skipped"
      fi
    fi
  fi
done

echo "Governance fragment:"
GOVERNANCE_SRC="$KIT_DIR/$GOVERNANCE_TMPL"
[[ -f "$GOVERNANCE_SRC" ]] || { echo "error: governance template '$GOVERNANCE_TMPL' not found at $GOVERNANCE_SRC" >&2; exit 1; }
render "$GOVERNANCE_SRC" | write "$TARGET/AGENTS.neyra-devkit.md"
say "AGENTS.neyra-devkit.md"
# Auto-wire the transparency + gate block into the repo's AGENTS.md (or CLAUDE.md). Idempotent.
wired=""
for inc in AGENTS.md CLAUDE.md; do
  incf="$TARGET/$inc"; [[ -f "$incf" ]] || continue
  wired=1
  if grep -q "Engineering process (neyra-dev-kit)" "$incf" 2>/dev/null; then say "$inc already has the kit block — left as is"
  elif [[ $DRY -eq 1 ]]; then say "[dry] append inline kit block to $inc"
  else
    blk="$(mktemp)"; render "$KIT_DIR/templates/AGENTS.include.md.tmpl" > "$blk"; cat "$blk" >> "$incf"; rm -f "$blk"  # atomic: render fully, then append
    say "appended inline kit block (transparency + gate) to $inc"
  fi
  break
done
[[ -z "$wired" && $DRY -eq 0 ]] && say "WARN: no AGENTS.md/CLAUDE.md in $TARGET — reference AGENTS.neyra-devkit.md manually"

for srv in "${MCP_SERVERS[@]}"; do
  if [[ "$srv" == "neyra" && "$ENABLE_NEYRA_MCP" == "1" ]]; then
    echo "MCP — project-scoped Neyra server (.mcp.json):"
    if [[ ! -f "$NEYRA_MCP_ENTRY" ]]; then
      say "WARN: canonical MCP server not found at $NEYRA_MCP_ENTRY — skipping"
    else
      rendered_mcp="$(render "$KIT_DIR/mcp/neyra.mcp.json.tmpl")"
      dest="$TARGET/.mcp.json"
      if [[ $DRY -eq 1 ]]; then
        say "[dry] merge 'neyra' server into $dest"
      elif [[ -f "$dest" ]] && command -v jq >/dev/null 2>&1; then
        cp "$dest" "$dest.bak"
        tmp="$(mktemp)"; tmpnew="$(mktemp)"; printf '%s' "$rendered_mcp" > "$tmpnew"
        if jq -s '.[0] * .[1]' "$dest" "$tmpnew" > "$tmp"; then mv "$tmp" "$dest"; else rm -f "$tmp" "$tmpnew"; echo "error: jq merge failed; .mcp.json unchanged (backup .mcp.json.bak)" >&2; exit 1; fi
        rm -f "$tmpnew"
        say "merged 'neyra' into .mcp.json (backup .mcp.json.bak; other servers preserved)"
      else
        printf '%s\n' "$rendered_mcp" > "$dest"; say "wrote $dest"
      fi
      # .mcp.json embeds a machine-local absolute path → keep it out of git.
      grep -qxF '.mcp.json' "$TARGET/.gitignore" 2>/dev/null || printf '.mcp.json\n' >> "$TARGET/.gitignore"
      say ".mcp.json gitignored (contains a machine-local path; secrets stay as \${ENV} placeholders)"
    fi
  elif [[ "$srv" == "firebase" && "$ENABLE_FIREBASE_MCP" == "1" ]]; then
    echo "MCP — official Firebase growth server (.mcp.json):"
    if [[ -z "$FIREBASE_MCP_DIR" || ! -f "$FIREBASE_MCP_DIR/firebase.json" ]]; then
      say "WARN: FIREBASE_PROJECT_DIR must resolve to a directory containing firebase.json — skipping"
    else
      rendered_mcp="$(render "$KIT_DIR/mcp/firebase.mcp.json.tmpl")"
      dest="$TARGET/.mcp.json"
      if [[ $DRY -eq 1 ]]; then
        say "[dry] merge 'firebase' server into $dest"
      elif [[ -f "$dest" ]] && command -v jq >/dev/null 2>&1; then
        tmp="$(mktemp)"; tmpnew="$(mktemp)"; printf '%s' "$rendered_mcp" > "$tmpnew"
        if jq -s '.[0] * .[1]' "$dest" "$tmpnew" > "$tmp"; then mv "$tmp" "$dest"; else rm -f "$tmp" "$tmpnew"; echo "error: jq merge failed; .mcp.json unchanged" >&2; exit 1; fi
        rm -f "$tmpnew"
        say "merged 'firebase' into .mcp.json (other servers preserved)"
      elif [[ -f "$dest" ]]; then
        say "WARN: jq is required to preserve existing MCP servers — skipping Firebase MCP"
        continue
      else
        printf '%s\n' "$rendered_mcp" > "$dest"; say "wrote $dest"
      fi
      grep -qxF '.mcp.json' "$TARGET/.gitignore" 2>/dev/null || printf '.mcp.json\n' >> "$TARGET/.gitignore"
      say ".mcp.json gitignored (machine-local project path; authentication stays in Firebase CLI or ADC)"
    fi
  fi
done

# Project-owned MCP connectors: settings/mcp/<name>.mcp.json.tmpl (tracked, declarative) →
# jq-merged into .mcp.json. Same primitive as the neyra server above; CONNECTORS.md stays
# human-readable prose, the .tmpl is the machine-readable registration. Templates are static
# JSON — secrets/paths stay as ${ENV} placeholders (Claude Code expands at runtime; no
# install-time {{token}} substitution, so any server shape works without touching render()).
echo "Project MCP connectors — settings/mcp/*.mcp.json.tmpl → .mcp.json:"
PROJ_MCP="$TARGET/settings/mcp"
if [[ -d "$PROJ_MCP" ]]; then
  for tf in "$PROJ_MCP"/*.mcp.json.tmpl; do
    [[ -e "$tf" ]] || continue
    name="$(basename "$tf" .mcp.json.tmpl)"
    dest="$TARGET/.mcp.json"
    if [[ $DRY -eq 1 ]]; then
      say "[dry] merge '$name' server into $dest"
    elif [[ -f "$dest" ]] && command -v jq >/dev/null 2>&1; then
      cp "$dest" "$dest.bak"
      tmp="$(mktemp)"
      if jq -s '.[0] * .[1]' "$dest" "$tf" > "$tmp"; then mv "$tmp" "$dest"; else rm -f "$tmp"; echo "error: jq merge failed for '$name'; .mcp.json unchanged (backup .mcp.json.bak)" >&2; exit 1; fi
      say "merged '$name' into .mcp.json (backup .mcp.json.bak; other servers preserved)"
    else
      cp "$tf" "$dest"; say "wrote $dest ('$name')"
    fi
    grep -qxF '.mcp.json' "$TARGET/.gitignore" 2>/dev/null || printf '.mcp.json\n' >> "$TARGET/.gitignore"
  done
else
  say "no settings/mcp/ — nothing to generate (add settings/mcp/<name>.mcp.json.tmpl to register a project MCP server; document it in settings/CONNECTORS.md)"
fi

# Hooks + bootstrap — deterministic enforcement surfaces (NEB-1321/1316).
# Copies the self-contained tooling the hooks depend on, then wires the hooks into
# the target's .claude/settings.json (append, never clobber; idempotent).
if [[ "${ENABLE_HOOKS}" == "1" ]]; then
  echo "Hooks — bootstrap + enforcement (.claude/settings.json):"
  tool_dst="$TARGET/agents/neyra-dev-kit"
  if [[ $DRY -eq 1 ]]; then
    say "[dry] copy hooks/, KIT_BOOTSTRAP.md, doctor.sh, lint-*.py, check-skill-mapping.py, VERSION → $tool_dst"
  else
    mkdir -p "$tool_dst/hooks/lib"
    if cp "$KIT_DIR"/hooks/*.sh "$tool_dst/hooks/" 2>/dev/null; then chmod +x "$tool_dst"/hooks/*.sh; fi
    cp "$KIT_DIR"/hooks/lib/*.sh "$tool_dst/hooks/lib/" 2>/dev/null || true   # the host I/O shim the hooks source
    for f in KIT_BOOTSTRAP.md doctor.sh source-policy.py lint-skills.py check-skill-mapping.py test-check-skill-mapping.py test-portable-reviewers.py check-egress.py lint-scope.py test-lint-scope.py check-external-leaks.py test-external-leaks.py lint-plans.py validate-codex-hooks.py VERSION; do
      [[ -f "$KIT_DIR/$f" ]] && cp "$KIT_DIR/$f" "$tool_dst/$f"
    done
    if [[ -d "$KIT_DIR/orchestration" ]]; then mkdir -p "$tool_dst/orchestration"; cp "$KIT_DIR"/orchestration/* "$tool_dst/orchestration/" 2>/dev/null || true; fi   # goal-mode driver + README
    chmod +x "$tool_dst/doctor.sh" 2>/dev/null || true
    say "copied hook scripts + doctor + linters into agents/neyra-dev-kit/"
  fi
  hooks_json='{"SessionStart":[{"hooks":[{"type":"command","command":"\"$CLAUDE_PROJECT_DIR/agents/neyra-dev-kit/hooks/session-start.sh\""}]}],"PreToolUse":[{"matcher":"Edit|Write|MultiEdit","hooks":[{"type":"command","command":"\"$CLAUDE_PROJECT_DIR/agents/neyra-dev-kit/hooks/pre-tool-use-guard.sh\""}]},{"matcher":"Task","hooks":[{"type":"command","command":"\"$CLAUDE_PROJECT_DIR/agents/neyra-dev-kit/hooks/count-task.sh\""}]}],"PostToolUse":[{"matcher":"Edit|Write|MultiEdit","hooks":[{"type":"command","command":"\"$CLAUDE_PROJECT_DIR/agents/neyra-dev-kit/hooks/post-tool-use-format.sh\""}]}],"Stop":[{"hooks":[{"type":"command","command":"\"$CLAUDE_PROJECT_DIR/agents/neyra-dev-kit/hooks/stop-gate.sh\""}]}]}'
  sdst="$TARGET/.claude/settings.json"
  if [[ $DRY -eq 1 ]]; then
    say "[dry] wire 4 hooks (SessionStart/PreToolUse/PostToolUse/Stop) into $sdst"
  elif grep -q 'neyra-dev-kit/hooks' "$sdst" 2>/dev/null; then
    say "settings.json already wires neyra-dev-kit hooks — left as is"
  elif [[ -f "$sdst" ]] && command -v jq >/dev/null 2>&1; then
    cp "$sdst" "$sdst.bak"
    tmp="$(mktemp)"
    if jq --argjson add "$hooks_json" '.hooks = (.hooks // {}) | reduce ($add|to_entries[]) as $e (.; .hooks[$e.key] = ((.hooks[$e.key] // []) + $e.value))' "$sdst" > "$tmp"; then
      mv "$tmp" "$sdst"; say "merged hooks into settings.json (backup .bak; existing hooks preserved)"
    else rm -f "$tmp"; say "WARN: jq merge failed; settings.json unchanged (backup .bak)"; fi
  else
    mkdir -p "$TARGET/.claude"
    if command -v jq >/dev/null 2>&1; then printf '{"hooks":%s}' "$hooks_json" | jq . > "$sdst"; else printf '{"hooks":%s}\n' "$hooks_json" > "$sdst"; fi
    say "wrote .claude/settings.json with hooks"
  fi

  # Cursor surface — hooks.json + always-apply bootstrap rule (Cursor uses a rule
  # for always-on context instead of a SessionStart hook).
  if [[ "${ENABLE_CURSOR_HOOKS:-1}" == "1" ]]; then
    if [[ $DRY -eq 1 ]]; then
      say "[dry] write .cursor/hooks.json + .cursor/rules/neyra-kit-bootstrap.mdc"
    else
      mkdir -p "$TARGET/.cursor/rules"
      cp "$KIT_DIR/templates/cursor/hooks.json" "$TARGET/.cursor/hooks.json"
      { printf -- '---\ndescription: Neyra dev-kit core — mandatory gates and skill rules\nalwaysApply: true\n---\n\n'; cat "$tool_dst/KIT_BOOTSTRAP.md"; } > "$TARGET/.cursor/rules/neyra-kit-bootstrap.mdc"
      say "wrote .cursor/hooks.json + bootstrap rule"
    fi
  fi

  # Codex surface — current hooks.json schema (event → matcher group → command).
  # Project hooks are skipped until the user trusts their exact definitions.
  if [[ "${ENABLE_CODEX:-1}" == "1" ]]; then
    if [[ $DRY -eq 1 ]]; then
      say "[dry] write .codex/hooks.json"
    else
      mkdir -p "$TARGET/.codex"
      cp "$KIT_DIR/templates/codex/hooks.json" "$TARGET/.codex/hooks.json"
      say "wrote .codex/hooks.json"
      say "Codex: open /hooks, then review and trust the project hooks before relying on them"
    fi
  fi
fi

# Knowledge graph scaffold (skill `knowledge-graph`). Copies freshness tooling
# (always) + templates (only if absent) into docs/knowledge/, plus the CI workflow.
# Best-effort, never fails the install.
if [[ -d "$KIT_DIR/knowledge" ]]; then
  kdst="$TARGET/docs/knowledge"
  if [[ $DRY -eq 1 ]]; then
    say "[dry] scaffold docs/knowledge/ (memory_freshness.py, check_code_node.py, templates, CI)"
  else
    mkdir -p "$kdst" 2>/dev/null || true
    cp "$KIT_DIR/knowledge/memory_freshness.py" "$kdst/memory_freshness.py" 2>/dev/null || true
    cp "$KIT_DIR/knowledge/check_code_node.py" "$kdst/check_code_node.py" 2>/dev/null || true
    [[ -f "$kdst/knowledge-map.yml" ]] || cp "$KIT_DIR/knowledge/templates/knowledge-map.yml" "$kdst/knowledge-map.yml" 2>/dev/null || true
    [[ -f "$kdst/README.md" ]] || cp "$KIT_DIR/knowledge/templates/README.md" "$kdst/README.md" 2>/dev/null || true
    if [[ -f "$KIT_DIR/knowledge/templates/doc-freshness.yml" ]]; then
      mkdir -p "$TARGET/.github/workflows" 2>/dev/null || true
      [[ -f "$TARGET/.github/workflows/doc-freshness.yml" ]] || cp "$KIT_DIR/knowledge/templates/doc-freshness.yml" "$TARGET/.github/workflows/doc-freshness.yml" 2>/dev/null || true
    fi
    say "scaffolded docs/knowledge/ (freshness tooling + templates + CI; existing files kept)"
  fi
fi

# Doc-freshness routine spec (NEB-1366). install.sh cannot register a schedule
# (cron lives in the scheduler, not the file) — it STAGES the spec; the agent
# registers it weekly on first session (see KIT_BOOTSTRAP). Best-effort, never fails.
if [[ -f "$KIT_DIR/routines/doc-freshness.SKILL.md" ]]; then
  rdst="$TARGET/docs/knowledge/routines"
  if [[ $DRY -eq 1 ]]; then
    say "[dry] stage doc-freshness routine spec → $rdst/doc-freshness.SKILL.md"
  else
    mkdir -p "$rdst" 2>/dev/null \
      && sed "s#{{REPO_PATH}}#$TARGET#g" "$KIT_DIR/routines/doc-freshness.SKILL.md" > "$rdst/doc-freshness.SKILL.md" 2>/dev/null \
      && say "staged doc-freshness routine spec (register weekly via scheduler — cron is app-side)" || true
  fi
fi

do_ "printf '%s\n' '$VERSION' > '$TARGET/.neyra-dev-kit.version'"
if [[ -f "$TARGET/.neyra-kit-canonical" ]]; then
  python3 "$KIT_DIR/source-policy.py" --root "$TARGET" --require-canonical >/dev/null \
    || { echo "error: target carries an invalid canonical marker" >&2; exit 2; }
  [[ $DRY -eq 1 ]] || rm -f "$TARGET/.neyra-dev-kit.source"
  say "canonical source marker retained; consumer source stamp not written"
elif [[ $DRY -eq 1 ]]; then
  say "[dry] write .neyra-dev-kit.source → $CANONICAL_REMOTE@$SOURCE_REVISION"
else
  {
    printf 'repository=%s\n' "$CANONICAL_REMOTE"
    printf 'revision=%s\n' "$SOURCE_REVISION"
    printf 'version=%s\n' "$VERSION"
  } > "$TARGET/.neyra-dev-kit.source"
  say "stamped canonical source in .neyra-dev-kit.source"
fi
echo "Done. Next: add a line to $TARGET/AGENTS.md (or CLAUDE.md):"
echo "      See [AGENTS.neyra-devkit.md](AGENTS.neyra-devkit.md) for the shared skill stack."
