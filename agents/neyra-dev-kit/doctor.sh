#!/usr/bin/env bash
# neyra-dev-kit doctor — one command: "is the install consistent and un-drifted?"
# Unifies the kit's checks (skills lint, skill↔subagent mapping, plans lint) and
# asserts the deterministic-enforcement surfaces are wired (hooks) and present
# (decisionLog). Exit non-zero on any hard failure; WARN lines don't fail.
#
# Usage: agents/neyra-dev-kit/doctor.sh
set -uo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$KIT/../.." && pwd)"
cd "$ROOT"   # the python checkers resolve paths from cwd

fail=0
run() { local label="$1"; shift; echo "── $label"; if ! "$@"; then fail=1; fi; }

echo "neyra-dev-kit doctor v$(cat "$KIT/VERSION") — $ROOT"
run "skills lint"          python3 "$KIT/lint-skills.py"
run "skill↔subagent map"   python3 "$KIT/check-skill-mapping.py"
run "plans lint"           python3 "$KIT/lint-plans.py"

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

echo "── hooks"
if [ -f "$ROOT/.claude/settings.json" ] && grep -q '"SessionStart"' "$ROOT/.claude/settings.json"; then
  echo "ok: SessionStart hook wired (bootstrap force-injects the kit core)"
else
  echo "WARN: no SessionStart hook in .claude/settings.json — bootstrap won't auto-inject"
fi

echo "── decisionLog"
if [ -f "$KIT/decisionLog.md" ]; then echo "ok: decisionLog.md present"
else echo "note: no decisionLog.md yet (optional per-repo ADR — create on first durable decision)"; fi

# NEB-1375: the governance fragment's version footer must match VERSION —
# a stale footer means the fragment (or the stamp) didn't ship with the bump.
echo "── version stamp"
ver="$(cat "$KIT/VERSION")"
checked=0
for gf in "$KIT/AGENTS.devkit.md" "$ROOT/AGENTS.neyra-devkit.md"; do
  [ -f "$gf" ] || continue
  checked=1
  foot="$(grep -o 'kit-version: [0-9][0-9.]*' "$gf" | head -1 | cut -d' ' -f2)"
  if [ "$foot" = "$ver" ]; then
    echo "ok: $(basename "$gf") footer matches VERSION ($ver)"
  else
    echo "FAIL: $(basename "$gf") footer says '${foot:-none}' but VERSION is '$ver' — update the footer with the bump (EVOLVING-THE-KIT §4)"
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
for hc in ".cursor/hooks.json:Cursor" ".codex/hooks.json:Codex"; do
  f="${hc%%:*}"; n="${hc#*:}"; [ -f "$ROOT/$f" ] && echo "ok: $n hooks config present ($f)"
done

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
if python3 -c 'import json; print(json.dumps({"tool_input":{"command":"*** Begin Patch\n*** Update File: AGENTS.neyra-devkit.md\n@@\n-old\n+new\n*** End Patch\n"}}))' |
   NEYRA_HOOK_HOST=codex "$KIT/hooks/pre-tool-use-guard.sh" >/dev/null 2>"$err"; then
  echo "FAIL: PreToolUse did not block Codex apply_patch to AGENTS.neyra-devkit.md"
  fail=1
else
  status=$?
  if [ "$status" -eq 2 ] && grep -q "kit-managed" "$err"; then
    echo "ok: PreToolUse blocks Codex apply_patch to kit-managed files"
  else
    echo "FAIL: PreToolUse returned unexpected status for kit-managed Codex apply_patch ($status)"
    fail=1
  fi
fi
rm -f "$err"

echo ""
if [ "$fail" -eq 0 ]; then echo "doctor: OK"; else echo "doctor: FAILURES above"; fi
exit "$fail"
