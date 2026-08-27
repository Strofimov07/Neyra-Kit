# neyra-dev-kit config — growth kit example
# Copy to <yourrepo>.growth.sh and fill in the values.
REPO_NAME="my-repo"
STACK="Swift (iOS) + Django REST"
BUILD_VERIFY_CMD="xcodebuild test -scheme MyApp"
LOCALES="en ru"
I18N_MECHANISM="Localizable.strings"
CONTRACT_STACK="DRF + drf-spectacular (@extend_schema) + generated client"
LINEAR_WORKSPACE="your-workspace"
read -r -d '' LINEAR_ROUTING <<'EOF' || true
   - ASO / growth / analytics / finance — **Nebula Browser**
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
ENABLE_FIREBASE_MCP=0

# Doc-freshness CI workflow (docs/knowledge code→node check). Set to 0 if this repo
# deliberately does not want it — the decision then survives upgrades instead of the
# installer scaffolding it back every time.
ENABLE_DOC_FRESHNESS_WORKFLOW=1

FIREBASE_PROJECT_DIR="settings/firebase"
FIREBASE_MCP_ACCESS="limited"
FIREBASE_MCP_TOOLS="firebase_read_resources,remoteconfig_get_template,remoteconfig_update_template,crashlytics_get_issue,crashlytics_list_events,crashlytics_batch_get_events,crashlytics_list_notes,crashlytics_get_report"
FIREBASE_MCP_FEATURES="apphosting,auth,core,crashlytics,realtimedatabase,dataconnect,firestore,functions,messaging,remoteconfig,storage,developerknowledge"
