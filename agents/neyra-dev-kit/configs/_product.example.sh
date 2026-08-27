# neyra-dev-kit config — product kit example
# Copy to <yourrepo>.product.sh and fill in the values.
REPO_NAME="my-repo"
STACK="Swift (iOS) + Django REST"
BUILD_VERIFY_CMD="xcodebuild test -scheme MyApp"
LOCALES="en ru"
I18N_MECHANISM="Localizable.strings"
CONTRACT_STACK="DRF + drf-spectacular (@extend_schema) + generated client"
LINEAR_WORKSPACE="your-workspace"
read -r -d '' LINEAR_ROUTING <<'EOF' || true
   - product discovery / solution design / delivery — **Nebula Browser**
EOF
# Approved label taxonomy — linear-router enforces reuse-before-create, one axis per
# label, and a required description. Mutually-exclusive axes should be Linear label
# groups; cross-cutting marks are flag:value. Fill `area:*` with your product's domains.
read -r -d '' LINEAR_LABELS <<'EOF' || true
   - type (group, one per issue): type:bug, type:feature, type:improvement, type:subtask
   - status (group): status:blocked-external, status:blocked-governance
   - area (group — fill in your product's domains): area:...
   - flags (cross-cutting): boundary:execute, evidence:external, harness-evolution, obsolete
EOF
ENABLE_LINEAR_ROUTER=1
ENABLE_NEYRA_MCP=0

# Doc-freshness CI workflow (docs/knowledge code→node check). Set to 0 if this repo
# deliberately does not want it — the decision then survives upgrades instead of the
# installer scaffolding it back every time.
ENABLE_DOC_FRESHNESS_WORKFLOW=1

