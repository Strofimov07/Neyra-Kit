#!/usr/bin/env bash
# neyra-dev-kit subagent-launch counter (PreToolUse, matcher: Task).
#
# Purely observational: logs which subagent types actually fire (the kit's
# most direct performance signal — which skills earn their place). Never
# blocks, never fails: always exits 0.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/lib/host-io.sh"
nk_load

agent_type="$(nk_json tool_input.subagent_type)"
[ -z "$agent_type" ] && agent_type="unknown"
nk_metric subagent_launch type "$agent_type"
exit 0
