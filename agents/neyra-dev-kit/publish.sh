#!/usr/bin/env bash
# Compatibility tombstone for the retired monorepo -> external publication path.
set -u

cat >&2 <<'EOF'
publish.sh is retired: Neyra-Kit is now the canonical authoring repository.
Author and review shared kit changes directly in git@github.com:Strofimov07/Neyra-Kit.git.
Consumer repositories must upgrade through install.sh from a reviewed Neyra-Kit revision.
EOF
exit 2
