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
ENABLE_LINEAR_ROUTER=1
ENABLE_NEYRA_MCP=0
