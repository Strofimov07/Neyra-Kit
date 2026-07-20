#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


KIT = Path(__file__).resolve().parent
INSTALLER = KIT / "install.sh"
ADOPTION_GUIDE = KIT / "FIREBASE_GROWTH_ADOPTION.md"
FULL_FEATURES = (
    "apphosting,auth,core,crashlytics,realtimedatabase,dataconnect,firestore,"
    "functions,messaging,remoteconfig,storage,developerknowledge"
)


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


class FirebaseMCPInstallerTests(unittest.TestCase):
    def make_consumer(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        git(root, "init", "-q")
        (root / ".gitignore").write_text("", encoding="utf-8")
        (root / ".mcp.json").write_text(
            json.dumps({"mcpServers": {"existing": {"command": "true"}}}),
            encoding="utf-8",
        )
        firebase_dir = root / "settings" / "firebase"
        firebase_dir.mkdir(parents=True)
        (firebase_dir / "firebase.json").write_text("{}\n", encoding="utf-8")
        return tmp, root

    def write_config(self, root: Path, enabled: bool, access: str | None = None) -> Path:
        access_config = [] if access is None else [f'FIREBASE_MCP_ACCESS="{access}"']
        config = root / "consumer.sh"
        config.write_text(
            "\n".join(
                [
                    'REPO_NAME="firebase-test"',
                    'STACK="test"',
                    'BUILD_VERIFY_CMD="true"',
                    'LOCALES="en"',
                    'I18N_MECHANISM="none"',
                    'CONTRACT_STACK="none"',
                    'LINEAR_WORKSPACE="test"',
                    "ENABLE_LINEAR_ROUTER=0",
                    "ENABLE_NEYRA_MCP=0",
                    f"ENABLE_FIREBASE_MCP={int(enabled)}",
                    'FIREBASE_PROJECT_DIR="settings/firebase"',
                    *access_config,
                    'FIREBASE_MCP_TOOLS="firebase_read_resources,remoteconfig_get_template,remoteconfig_update_template,crashlytics_get_report"',
                    f'FIREBASE_MCP_FEATURES="{FULL_FEATURES}"',
                    "ENABLE_CURSOR_SKILLS=0",
                    "ENABLE_HOOKS=0",
                    "ENABLE_CODEX=0",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return config

    def run_install(self, root: Path, config: Path, *flags: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(INSTALLER), *flags, "growth", str(root), str(config)],
            capture_output=True,
            text=True,
        )

    def test_disabled_connector_leaves_existing_mcp_configuration_unchanged(self):
        tmp, root = self.make_consumer()
        with tmp:
            config = self.write_config(root, enabled=False)
            before = (root / ".mcp.json").read_text(encoding="utf-8")

            result = self.run_install(root, config)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(before, (root / ".mcp.json").read_text(encoding="utf-8"))

    def test_enabled_connector_renders_official_server_with_absolute_project_directory(self):
        tmp, root = self.make_consumer()
        with tmp:
            config = self.write_config(root, enabled=True)

            result = self.run_install(root, config)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            self.assertIn("existing", payload["mcpServers"])
            self.assertFalse((root / ".mcp.json.bak").exists())
            firebase = payload["mcpServers"]["firebase"]
            self.assertEqual("npx", firebase["command"])
            self.assertEqual(
                [
                    "-y",
                    "firebase-tools@latest",
                    "mcp",
                    "--dir",
                    str(root / "settings" / "firebase"),
                    "--tools",
                    "firebase_read_resources,remoteconfig_get_template,remoteconfig_update_template,crashlytics_get_report",
                ],
                firebase["args"],
            )
            serialized = json.dumps(firebase).lower()
            self.assertNotIn("firebase_token", serialized)
            self.assertNotIn("service-account", serialized)
            self.assertNotIn("credential", serialized)

    def test_full_connector_renders_all_feature_groups_without_a_tool_allowlist(self):
        tmp, root = self.make_consumer()
        with tmp:
            config = self.write_config(root, enabled=True, access="full")

            result = self.run_install(root, config)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
            self.assertEqual(
                [
                    "-y",
                    "firebase-tools@latest",
                    "mcp",
                    "--dir",
                    str(root / "settings" / "firebase"),
                    "--only",
                    FULL_FEATURES,
                ],
                payload["mcpServers"]["firebase"]["args"],
            )

    def test_full_connector_doctor_warns_about_side_effecting_authority(self):
        tmp, root = self.make_consumer()
        with tmp:
            config = self.write_config(root, enabled=True, access="full")

            result = self.run_install(root, config, "--doctor")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            output = result.stdout.lower()
            self.assertIn("full", output)
            self.assertIn("side-effecting", output)
            self.assertIn("per-action confirmation", output)

    def test_doctor_reports_auth_iam_and_codex_setup_without_credentials(self):
        tmp, root = self.make_consumer()
        with tmp:
            config = self.write_config(root, enabled=True)

            result = self.run_install(root, config, "--doctor")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            output = result.stdout.lower()
            self.assertIn("firebase mcp", output)
            self.assertIn("firebase login", output)
            self.assertIn("roles/cloudconfig.viewer", output)
            self.assertIn("roles/cloudconfig.admin", output)
            self.assertIn("codex mcp add firebase", output)
            self.assertNotIn("firebase_token", output)

    def test_cross_product_adoption_guide_separates_readiness_states(self):
        guide = ADOPTION_GUIDE.read_text(encoding="utf-8")
        lower = guide.lower()

        for required in (
            "tool-ready",
            "contract-ready",
            "measurement-verified",
            "experiment-ready",
            "experiment-live",
            "limited",
            "full",
            "event map",
            "correlation",
            "safe local default",
            "assignment event and denominator",
            "exact full-template diff",
            "explicit approval",
            "etag-aware",
            "firebase debugview",
            "backend mirror",
            "ga4",
            "bigquery",
            "rollback",
        ):
            self.assertIn(required, lower)

        self.assertNotIn("nebula70", lower)
        self.assertNotIn("ai browser", lower)


if __name__ == "__main__":
    unittest.main()
