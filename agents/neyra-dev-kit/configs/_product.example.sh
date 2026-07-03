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
ENABLE_LINEAR_ROUTER=1
ENABLE_NEYRA_MCP=0
