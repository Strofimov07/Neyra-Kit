#!/usr/bin/env bash
# neyra-dev-kit hook host I/O shim.
#
# The same four hook scripts run under Claude Code, Cursor, and Codex. Each host
# delivers a DIFFERENT stdin payload and expects a DIFFERENT "block" response, so
# the scripts stay logic-only and call these helpers for all I/O. Each host's hook
# config exports NEYRA_HOOK_HOST; unset defaults to `claude`, so the existing
# Claude Code wiring is byte-for-byte unchanged.
#
# Verified contracts (per each tool's hooks docs):
#   - Claude Code: PreToolUse blocks via exit 2 + stderr; Stop blocks via
#     {"decision":"block","reason"}; SessionStart injects
#     {"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext"}}.
#   - Codex: identical SessionStart + Stop schema; PreToolUse also honors exit 2 +
#     stderr (path lives in tool_input.command for apply_patch).
#   - Cursor: PreToolUse blocks via {"permission":"deny","user_message",...};
#     afterFileEdit is observational (used only for formatting); stop cannot block
#     but accepts {"followup_message"} to auto-continue (our gate equivalent).
set -uo pipefail

NK_HOST="${NEYRA_HOOK_HOST:-claude}"
NK_PAYLOAD=""

# Read the hook's stdin payload once; later helpers parse it.
nk_load() { NK_PAYLOAD="$(cat)"; }

# Print a dotted JSON field from the payload (scalars only; "" on miss/error).
nk_json() {
  printf '%s' "$NK_PAYLOAD" | python3 -c '
import json, sys
keys = sys.argv[1].split(".")
try:
    o = json.load(sys.stdin)
    for k in keys:
        if isinstance(o, dict) and k in o:
            o = o[k]
        else:
            o = ""; break
    print("" if isinstance(o, (dict, list)) else o)
except Exception:
    print("")' "$1" 2>/dev/null
}

# Resolve every path an Edit/Write tool is acting on, one per line. Claude Code
# and Cursor expose a single file_path; Codex apply_patch can carry many files in
# one command, so returning only its first header would let later files bypass
# guards and formatting.
nk_edit_paths() {
  local p
  case "$NK_HOST" in
    cursor)
      p="$(nk_json file_path)"; [ -n "$p" ] && { printf '%s\n' "$p"; return; }
      nk_json tool_input.file_path ;;
    codex)
      p="$(nk_json tool_input.file_path)"; [ -n "$p" ] && { printf '%s\n' "$p"; return; }
      # apply_patch: paths appear in the patch command text. Include move
      # destinations as edits too; a protected destination must not bypass the
      # guard merely because its source path is allowed.
      printf '%s' "$NK_PAYLOAD" | python3 -c '
import json, re, sys
try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception:
    cmd = ""
cmd = cmd if isinstance(cmd, str) else ""
paths = []

def add(path):
    path = path.strip()
    if path and path != "/dev/null" and path not in paths:
        paths.append(path)

for line in cmd.splitlines():
    match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
    if match:
        add(match.group(1))
        continue
    match = re.match(r"\*\*\* Move to: (.+)$", line)
    if match:
        add(match.group(1))

if not paths:
    for line in cmd.splitlines():
        match = re.match(r"(?:\+\+\+|---)\s+(.+)$", line)
        if not match:
            continue
        path = match.group(1).split("\t", 1)[0].strip()
        if path.startswith(("a/", "b/")):
            path = path[2:]
        add(path)

print("\n".join(paths))' 2>/dev/null ;;
    *)
      nk_json tool_input.file_path ;;
  esac
}

# Backward-compatible first-path helper for any external hook that still calls
# the old scalar API. Multi-file-aware hooks should use nk_edit_paths directly.
nk_edit_path() { nk_edit_paths | sed -n '1p'; }

# Block an attempted edit (PreToolUse guard). $1 = human reason. Exits.
nk_block_edit() {
  case "$NK_HOST" in
    cursor)
      python3 -c 'import json,sys; print(json.dumps({"permission":"deny","user_message":sys.argv[1],"agent_message":sys.argv[1]}))' "$1"
      exit 0 ;;
    *)  # claude + codex both honor exit 2 + stderr
      printf '%s\n' "$1" >&2
      exit 2 ;;
  esac
}

# Gate at stop when doctor failed: keep the agent going with the reason. Exits.
nk_block_stop() {
  case "$NK_HOST" in
    cursor)
      python3 -c 'import json,sys; print(json.dumps({"followup_message":sys.argv[1]}))' "$1" ;;
    *)  # claude + codex
      python3 -c 'import json,sys; print(json.dumps({"decision":"block","reason":sys.argv[1]}))' "$1" ;;
  esac
  exit 0
}

# True when this Stop hook is already a re-invocation after a prior block (thrash guard).
nk_stop_active() {
  local v
  case "$NK_HOST" in
    cursor) v="$(nk_json loop_count)"; [ -n "$v" ] && [ "$v" != "0" ] ;;
    *)      [ "$(nk_json stop_hook_active)" = "True" ] ;;
  esac
}

# Inject SessionStart bootstrap context. $1 = text. (Cursor uses an always-apply rule instead.)
nk_emit_context() {
  case "$NK_HOST" in
    cursor) : ;;
    *) python3 - "$1" <<'PY'
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": sys.argv[1]}}))
PY
       ;;
  esac
}

# --- kit telemetry (best-effort, never fails the hook) -----------------------
# Append one JSONL event to <repo>/.neyra/kit-metrics.jsonl. Local-only
# operational telemetry (.neyra/ is gitignored): which subagents fire, how often
# the stop-gate blocks, guard denials. Read by kit-metrics.py.
nk_metric() { # nk_metric <event> [key value]...
  local root="${CLAUDE_PROJECT_DIR:-}"
  [ -z "$root" ] && root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." 2>/dev/null && pwd)"
  [ -z "$root" ] && return 0
  local dir="$root/.neyra"
  mkdir -p "$dir" 2>/dev/null || return 0
  local ev="$1"; shift
  {
    printf '{"ts":"%s","host":"%s","event":"%s"' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$NK_HOST" "$ev"
    while [ $# -ge 2 ]; do printf ',"%s":"%s"' "$1" "$(printf '%s' "$2" | tr -d '"\\' | head -c 120)"; shift 2; done
    printf '}\n'
  } >> "$dir/kit-metrics.jsonl" 2>/dev/null || true
  return 0
}
