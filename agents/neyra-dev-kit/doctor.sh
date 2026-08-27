#!/usr/bin/env bash
# neyra-dev-kit doctor — one command: "is the install consistent and un-drifted?"
# Unifies the kit's checks (skills lint, skill↔subagent mapping, plans lint) and
# asserts the deterministic-enforcement surfaces are wired (hooks) and present
# (decisionLog). Exit non-zero on any hard failure; WARN lines don't fail.
#
# Usage: agents/neyra-dev-kit/doctor.sh [--fast]
#   (default)  full run — structural integrity PLUS the prose/frontmatter linters,
#              regressions, egress scan, Codex/Firebase/Impeccable smokes, and
#              branch hygiene. This is the CI + manual gate.
#   --fast     structural integrity only — source identity, hook wiring,
#              decisionLog, version stamp, multi-tool surfaces. The Stop gate
#              calls this (NEB-1612): the full run is fail-closed, and its prose
#              linters can reject a benign markdown (a quoted "TODO", a BOM, a
#              non-UTF-8 byte), which would then block *every* agent turn in the
#              repo. Structural checks can't be tripped by document content.
set -uo pipefail

FAST=0
for arg in "$@"; do
  case "$arg" in
    --fast) FAST=1 ;;
    -h|--help) sed -n '7,17p' "$0"; exit 0 ;;
    *) echo "doctor: unknown arg '$arg' (usage: doctor.sh [--fast])" >&2; exit 2 ;;
  esac
done

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$KIT/../.." && pwd)"
cd "$ROOT"   # the python checkers resolve paths from cwd

fail=0
run() { local label="$1"; shift; echo "── $label"; if ! "$@"; then fail=1; fi; }

mode="full"; [ "$FAST" -eq 1 ] && mode="fast"
echo "neyra-dev-kit doctor v$(cat "$KIT/VERSION") [$mode] — $ROOT"

# ─────────────────────────────────────────────────────────────────────────────
# Structural integrity — always run, in both --fast and full. These check the
# shape of the install (identity, wiring, presence, version stamp); none of them
# can be tripped by the *content* of a document, so they are safe on the Stop gate.
# ─────────────────────────────────────────────────────────────────────────────
echo "── source policy"
if [ -f "$ROOT/.neyra-kit-canonical" ]; then
  run "canonical authoring identity" python3 "$KIT/source-policy.py" --root "$ROOT" --require-canonical
elif [ -f "$ROOT/.neyra-dev-kit.source" ]; then
  run "consumer source identity" python3 "$KIT/source-policy.py" --root "$ROOT"
else
  echo "WARN: no canonical marker or consumer source stamp — re-install from Neyra-Kit"
fi

echo "── hooks"
if [ -f "$ROOT/.claude/settings.json" ] && grep -q '"SessionStart"' "$ROOT/.claude/settings.json"; then
  echo "ok: SessionStart hook wired (bootstrap force-injects the kit core)"
else
  echo "WARN: no SessionStart hook in .claude/settings.json — bootstrap won't auto-inject"
fi

echo "── decisionLog"
if [ -f "$KIT/decisionLog.md" ]; then
  echo "ok: decisionLog.md present"
elif [ -f "$ROOT/.neyra-kit-canonical" ]; then
  echo "FAIL: canonical Neyra-Kit requires decisionLog.md"
  fail=1
else
  echo "note: decisionLog.md is canonical-source history and is not copied to consumers"
fi

# NEB-1375 / NEB-1484: the governance fragment's version footer must match VERSION.
# The footer renders from VERSION at install ({{KIT_VERSION}}), so every consumer's
# fragment matches its installed version across all profiles and no manual per-release
# footer bump is needed. In the canonical repo the template is read raw, so the
# unrendered placeholder is the expected, correct state.
echo "── version stamp"
ver="$(cat "$KIT/VERSION")"
checked=0
for gf in "$KIT/AGENTS.devkit.md" "$ROOT/AGENTS.neyra-devkit.md"; do
  [ -f "$gf" ] || continue
  checked=1
  if grep -q 'kit-version: {{KIT_VERSION}}' "$gf"; then
    echo "ok: $(basename "$gf") footer renders VERSION at install ({{KIT_VERSION}})"
    continue
  fi
  foot="$(grep -o 'kit-version: [0-9][0-9.]*' "$gf" | head -1 | cut -d' ' -f2)"
  if [ "$foot" = "$ver" ]; then
    echo "ok: $(basename "$gf") footer matches VERSION ($ver)"
  else
    echo "FAIL: $(basename "$gf") footer says '${foot:-none}' but VERSION is '$ver' — footer should be {{KIT_VERSION}} (rendered at install) or match VERSION"
    fail=1
  fi
done
[ "$checked" -eq 0 ] && echo "note: no governance fragment found to check"

echo "── multi-tool surfaces"
if [ -f "$KIT/hooks/lib/host-io.sh" ]; then echo "ok: host I/O shim present (Claude Code + Cursor + Codex)"
else echo "WARN: hooks/lib/host-io.sh missing — multi-host hooks will fail to source (re-run install.sh)"; fi
[ -f "$KIT/orchestration/goal-mode.workflow.js" ] && echo "ok: goal-mode driver present (Claude Code Workflow engine)"
for pair in "Cursor:.cursor/skills" "Codex:.agents/skills"; do
  name="${pair%%:*}"; dir="${pair#*:}"
  [ -d "$ROOT/$dir" ] && echo "ok: $name skills mirror present ($dir, $(find "$ROOT/$dir" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l | tr -d ' ') entries)"
done
if [ -d "$ROOT/settings/skills" ]; then
  for d in "$ROOT/settings/skills"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    sid="$(basename "$d")"
    if [ -d "$ROOT/.claude/skills/$sid" ]; then echo "ok: project skill '$sid' surfaced (.claude/skills/$sid)"
    else echo "WARN: project skill '$sid' in settings/skills/ but not surfaced — re-run install.sh"; fi
  done
fi
[ -f "$ROOT/.cursor/hooks.json" ] && echo "ok: Cursor hooks config present (.cursor/hooks.json)"

if [ "$FAST" -eq 1 ]; then
  echo ""
  if [ "$fail" -eq 0 ]; then echo "doctor: OK [fast]"; else echo "doctor: FAILURES above [fast]"; fi
  exit "$fail"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Full run only — prose/frontmatter linters, regressions, egress, host smokes,
# network-touching branch hygiene. These can legitimately fail on document
# content, so they are kept off the per-turn Stop gate and run in CI + manually.
# ─────────────────────────────────────────────────────────────────────────────
if [ -f "$ROOT/.neyra-kit-canonical" ] && [ -f "$KIT/test-source-policy.py" ]; then
  run "source-policy regression" python3 "$KIT/test-source-policy.py"
  run "canonical leak scan" python3 "$KIT/check-external-leaks.py" "$ROOT"
  [ -f "$KIT/test-retire.py" ] && run "retire regression" python3 "$KIT/test-retire.py"
  [ -f "$KIT/test-reconcile.py" ] && run "reconcile regression" python3 "$KIT/test-reconcile.py"
  [ -f "$KIT/test-product-profile.py" ] && run "product-profile regression" python3 "$KIT/test-product-profile.py"
  [ -f "$KIT/test-optional-artifacts.py" ] && run "optional-artifacts regression" python3 "$KIT/test-optional-artifacts.py"
  [ -f "$KIT/test-repo-hygiene.py" ] && run "repo-hygiene regression" python3 "$KIT/test-repo-hygiene.py"
  [ -f "$KIT/test-profile-gating.py" ] && run "profile-gating regression" python3 "$KIT/test-profile-gating.py"
fi
# ─────────────────────────────────────────────────────────────────────────────
# Product profile + project-fact anchors (advisory — never fail the run).
# A gate whose facts file is absent silently degrades to generic advice, which
# is the "dead anchor" failure the kit already learned once: the skill routes
# somewhere that does not exist and nobody sees the no-op.
# ─────────────────────────────────────────────────────────────────────────────
if [ -f "$KIT/product-profile.py" ]; then
  echo "── product profile"
  python3 "$KIT/product-profile.py" "$ROOT" || true
fi
# Structural drift, advisory (v0.41.0). These two shipped in v0.40.0 with no caller,
# which made them unreachable: an agent in a consumer repo has no way to learn a script
# exists. Reported here, never fail the run — their thresholds are per-repo judgment,
# so --strict stays a deliberate CI choice, not a default.
# The kit's own vendored design-skill bundles are excluded by the CALLER: the tool stays
# generic, the paths that are kit-specific live here.
if [ -f "$KIT/check-repo-hygiene.py" ]; then
  echo "── repo hygiene (advisory)"
  python3 "$KIT/check-repo-hygiene.py" "$ROOT" || true
fi
if [ -f "$KIT/check-module-size.py" ]; then
  echo "── modularity drift (advisory)"
  python3 "$KIT/check-module-size.py" "$ROOT" \
    --exclude agents/design-skills --exclude .claude/skills || true
fi
if [ -d "$ROOT/agents/dev-skills" ] || [ -d "$ROOT/.claude/agents" ]; then
  if grep -rqs "settings/facts" "$ROOT/agents/dev-skills" "$ROOT/.claude/agents" 2>/dev/null; then
    if [ ! -d "$ROOT/settings/facts" ]; then
      echo "── project facts"
      echo "WARN: installed skills reference settings/facts/ but the directory does not exist —"
      echo "      those skills degrade to generic advice. Create it and add the files they name."
    fi
  fi
fi

run "skills lint"          python3 "$KIT/lint-skills.py"
run "skill-mapping regression" python3 "$KIT/test-check-skill-mapping.py"
# NEB-1484: the portable-reviewer regression validates pr-review-watch + security-review —
# dev-only skills a non-dev bundle (product/growth/mgmt) does not ship. Run it only where
# they are expected: the canonical repo, or a consumer whose installed kit is `dev`
# (recorded as kit= in .neyra-dev-kit.source). Elsewhere it would FileNotFoundError into a
# false-negative doctor result.
kit_profile=""
[ -f "$ROOT/.neyra-dev-kit.source" ] && kit_profile="$(sed -n 's/^kit=//p' "$ROOT/.neyra-dev-kit.source" | head -1)"
if [ -f "$ROOT/.neyra-kit-canonical" ] || [ "$kit_profile" = "dev" ]; then
  run "portable-reviewer regression" python3 "$KIT/test-portable-reviewers.py"
else
  echo "── portable-reviewer regression"
  echo "note: skip — non-dev bundle (kit='${kit_profile:-unspecified}') ships no pr-review-watch/security-review"
fi
run "skill↔subagent map"   python3 "$KIT/check-skill-mapping.py"
run "plans lint"           python3 "$KIT/lint-plans.py"
run "bundled-skill egress" python3 "$KIT/check-egress.py"
run "scope-lint regression" python3 "$KIT/test-lint-scope.py"
run "gate-resolution regression" python3 "$KIT/test-gate-resolution.py"
run "cross-ref anchors"    python3 "$KIT/check-cross-refs.py"
run "cross-ref regression" python3 "$KIT/test-cross-refs.py"
run "external-leak regression" python3 "$KIT/test-external-leaks.py"
if [ -f "$KIT/test-codex-hooks.py" ]; then
  run "Codex hook regression" python3 "$KIT/test-codex-hooks.py"
fi
if [ -f "$KIT/test-firebase-mcp.py" ]; then
  run "Firebase MCP regression" python3 "$KIT/test-firebase-mcp.py"
fi
if [ -f "$ROOT/agents/design-skills/impeccable/scripts/live-server.security.test.mjs" ]; then
  if command -v node >/dev/null 2>&1; then
    run "impeccable live security" node --test "$ROOT/agents/design-skills/impeccable/scripts/live-server.security.test.mjs"
  else
    echo "WARN: node not found — skip Impeccable live-server security regression"
  fi
fi

echo "── branch hygiene"
# Merged branches must not accumulate on origin (pr-hygiene: "Clean up after
# merge"). Offline check against last-fetched refs — no network; if a branch
# is already deleted on the remote but the ref lingers, git fetch -p heals it.
if git rev-parse --git-dir >/dev/null 2>&1 && git remote get-url origin >/dev/null 2>&1; then
  target=""
  git show-ref --verify --quiet refs/remotes/origin/dev && target="origin/dev"
  [ -z "$target" ] && git show-ref --verify --quiet refs/remotes/origin/main && target="origin/main"
  if [ -n "$target" ]; then
    stale="$(git branch -r --merged "$target" 2>/dev/null | grep -vE "origin/(dev|main|HEAD)" | sed 's/^ *//')"
    if [ -n "$stale" ]; then
      echo "FAIL: merged branches still on origin (vs $target) — git fetch -p, then git push origin --delete <branch>:"
      printf '%s\n' "$stale" | sed 's/^/   ✗ /'
      fail=1
    else
      echo "ok: no merged branches left on origin (vs $target, refs as of last fetch)"
    fi
  else
    echo "note: no origin/dev or origin/main ref — skip branch hygiene"
  fi
else
  echo "note: not a git repo with origin — skip branch hygiene"
fi

codex_template="$KIT/templates/codex/hooks.json"
codex_installed="$ROOT/.codex/hooks.json"
if [ -f "$codex_template" ]; then
  run "Codex hook template" python3 "$KIT/validate-codex-hooks.py" "$codex_template"
fi
if [ -f "$codex_installed" ]; then
  run "Codex installed hooks" python3 "$KIT/validate-codex-hooks.py" "$codex_installed"
  echo "note: Codex only runs project hooks after their current definitions are reviewed and trusted in /hooks"
else
  echo "WARN: no Codex hooks config at .codex/hooks.json — re-run install.sh"
fi

echo "── codex hook smoke"
if out="$(NEYRA_HOOK_HOST=codex "$KIT/hooks/session-start.sh" </dev/null)" &&
   printf '%s' "$out" | python3 -c 'import json,sys; o=json.load(sys.stdin); assert o["hookSpecificOutput"]["hookEventName"] == "SessionStart"; assert o["hookSpecificOutput"]["additionalContext"]' >/dev/null 2>&1; then
  echo "ok: SessionStart emits Codex context JSON"
else
  echo "FAIL: SessionStart did not emit valid Codex context JSON"
  fail=1
fi
if printf '{"tool_input":{"file_path":"src/main.py"}}' | NEYRA_HOOK_HOST=codex "$KIT/hooks/pre-tool-use-guard.sh" >/dev/null 2>&1; then
  echo "ok: PreToolUse allows normal Codex file edits"
else
  echo "FAIL: PreToolUse blocked a normal Codex file edit"
  fail=1
fi
err="$(mktemp)"
if python3 -c 'import json; print(json.dumps({"tool_input":{"command":"*** Begin Patch\n*** Update File: src/allowed.py\n@@\n-old\n+new\n*** Update File: AGENTS.neyra-devkit.md\n@@\n-old\n+new\n*** End Patch\n"}}))' |
   NEYRA_HOOK_HOST=codex "$KIT/hooks/pre-tool-use-guard.sh" >/dev/null 2>"$err"; then
  echo "FAIL: PreToolUse did not block a later kit-managed file in Codex apply_patch"
  fail=1
else
  status=$?
  if [ "$status" -eq 2 ] && grep -q "kit-managed" "$err"; then
    echo "ok: PreToolUse blocks any kit-managed path in multi-file Codex apply_patch"
  else
    echo "FAIL: PreToolUse returned unexpected status for kit-managed Codex apply_patch ($status)"
    fail=1
  fi
fi
rm -f "$err"

echo "── cursor hook smoke"
# NEB-1613: Cursor supports `preToolUse` (confirmed against Cursor's current hook
# docs), so the shipped `.cursor/hooks.json` guard is valid — but doctor used to
# report the Cursor config OK from file existence alone, which cannot catch a config
# the host ignores (the false-green this closes). Mirror the Codex behavioural smoke:
# the guard must ALLOW a normal edit and DENY a kit-managed path. Cursor blocks with
# `{"permission":"deny"}` on exit 0 (not exit 2 like Claude/Codex), so assert on the
# emitted JSON, not the exit code.
if printf '{"file_path":"src/main.py"}' | NEYRA_HOOK_HOST=cursor "$KIT/hooks/pre-tool-use-guard.sh" 2>/dev/null |
   python3 -c 'import json,sys; raw=sys.stdin.read().strip(); d=json.loads(raw) if raw else {}; sys.exit(1 if d.get("permission")=="deny" else 0)'; then
  echo "ok: Cursor PreToolUse allows normal file edits"
else
  echo "FAIL: Cursor PreToolUse denied a normal file edit"
  fail=1
fi
if printf '{"file_path":"AGENTS.neyra-devkit.md"}' | NEYRA_HOOK_HOST=cursor "$KIT/hooks/pre-tool-use-guard.sh" 2>/dev/null |
   python3 -c 'import json,sys; raw=sys.stdin.read().strip(); d=json.loads(raw) if raw else {}; sys.exit(0 if d.get("permission")=="deny" else 1)'; then
  echo "ok: Cursor PreToolUse blocks a kit-managed path (permission:deny)"
else
  echo "FAIL: Cursor PreToolUse did not block a kit-managed path (guard inert under Cursor)"
  fail=1
fi

echo "── goal-mode gate smoke"
# NEB-1589: the checkpoint-1 gate must block Task/Workflow dispatch while awaiting
# approval, allow once approved, and never fire when goal-mode is inactive (no gate).
gdir="$(mktemp -d)"; mkdir -p "$gdir/.neyra"
printf 'awaiting-checkpoint-1\n' > "$gdir/.neyra/goal-mode.gate"
if printf '{"tool_input":{"subagent_type":"implementation-loop"}}' | CLAUDE_PROJECT_DIR="$gdir" "$KIT/hooks/count-task.sh" >/dev/null 2>&1; then
  echo "FAIL: goal-mode gate did not block dispatch while awaiting checkpoint 1"; fail=1
else
  echo "ok: goal-mode gate blocks dispatch while awaiting checkpoint 1"
fi
printf 'approved\n' > "$gdir/.neyra/goal-mode.gate"
if printf '{"tool_input":{"subagent_type":"implementation-loop"}}' | CLAUDE_PROJECT_DIR="$gdir" "$KIT/hooks/count-task.sh" >/dev/null 2>&1; then
  echo "ok: goal-mode gate allows dispatch after checkpoint 1 approved"
else
  echo "FAIL: goal-mode gate blocked dispatch after approval"; fail=1
fi
rm -f "$gdir/.neyra/goal-mode.gate"
if printf '{"tool_input":{"subagent_type":"implementation-loop"}}' | CLAUDE_PROJECT_DIR="$gdir" "$KIT/hooks/count-task.sh" >/dev/null 2>&1; then
  echo "ok: no gate → normal dispatch (no false positive)"
else
  echo "FAIL: dispatch blocked with no goal-mode gate present (false positive)"; fail=1
fi
rm -rf "$gdir"

echo ""
if [ "$fail" -eq 0 ]; then echo "doctor: OK"; else echo "doctor: FAILURES above"; fi
exit "$fail"
