#!/usr/bin/env bash
# neyra-dev-kit Stop gate.
#
# When the main agent stops, run `kit doctor` (fast kit-consistency check). If it
# fails, keep the agent going with the reason so the drift gets fixed before
# finishing. Thrash-safe: exits immediately when already re-invoked by a prior
# block, so it can never loop. Host-aware via the shim (Claude/Codex emit
# {"decision":"block"}; Cursor emits {"followup_message"}). Repos can extend
# doctor with their own lint/test for a stricter gate.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib/host-io.sh"
KIT="$(cd "$DIR/.." && pwd)"
nk_load

nk_stop_active && exit 0

if out="$("$KIT/doctor.sh" 2>&1)"; then
  # Post-merge CI net (NEB-1403): if the default branch's latest completed CI
  # run turned red, block ONCE per session (marker = thrash-safe) so a silent
  # post-merge failure is caught at the session boundary even when nobody
  # invoked post-merge-watch. Best-effort: no gh / no CI / API error → skip.
  # NEYRA_FAKE_CI_STATUS overrides the lookup for deterministic testing.
  ROOT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$DIR/../../.." && pwd)}"
  CI_MARKER="$ROOT_DIR/.neyra/ci-red-warned"
  if [ ! -f "$CI_MARKER" ]; then
    ci_status="${NEYRA_FAKE_CI_STATUS:-}"
    if [ -z "$ci_status" ] && command -v gh >/dev/null 2>&1 && [ -d "$ROOT_DIR/.github/workflows" ]; then
      def_branch="$(git -C "$ROOT_DIR" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|origin/||')"
      ci_status="$(cd "$ROOT_DIR" && timeout 8 gh run list --branch "${def_branch:-main}" --status completed --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || true)"
    fi
    if [ "$ci_status" = "failure" ]; then
      mkdir -p "$ROOT_DIR/.neyra" 2>/dev/null && touch "$CI_MARKER" 2>/dev/null
      nk_metric stop_gate result ci_red
      nk_block_stop "post-merge-watch net: the default branch's latest CI run is RED. Check it before finishing (gh run list --limit 3) — a merge this session may have broken it. This warns once per session."
    fi
  fi
  nk_metric stop_gate result ok
  exit 0
else
  nk_metric stop_gate result blocked
  nk_block_stop "neyra-dev-kit doctor failed — fix kit drift before finishing:
$(printf '%s' "$out" | tail -20)"
fi
