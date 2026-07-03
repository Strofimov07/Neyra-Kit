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
  nk_metric stop_gate result ok
  exit 0
else
  nk_metric stop_gate result blocked
  nk_block_stop "neyra-dev-kit doctor failed — fix kit drift before finishing:
$(printf '%s' "$out" | tail -20)"
fi
