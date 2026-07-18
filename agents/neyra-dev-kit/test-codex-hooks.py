#!/usr/bin/env python3
"""Regression tests for the published Codex hook registration contract."""

import json
import os
import pathlib
import subprocess
import tempfile
import unittest


KIT = pathlib.Path(__file__).resolve().parent
TEMPLATE = KIT / "templates" / "codex" / "hooks.json"
HOOKS = KIT / "hooks"


class CodexHookConfigTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_template_uses_current_nested_codex_schema(self):
        self.assertEqual(set(self.config), {"hooks"})
        events = self.config["hooks"]
        self.assertEqual(
            set(events), {"SessionStart", "PreToolUse", "PostToolUse", "Stop"}
        )

        for event, groups in events.items():
            self.assertIsInstance(groups, list, event)
            self.assertTrue(groups, event)
            for group in groups:
                self.assertIsInstance(group.get("hooks"), list, event)
                self.assertTrue(group["hooks"], event)
                for handler in group["hooks"]:
                    self.assertEqual(handler.get("type"), "command", event)

    def test_edit_hooks_match_apply_patch_aliases(self):
        self.assertIn("hooks", self.config)
        events = self.config["hooks"]
        self.assertEqual(events["PreToolUse"][0]["matcher"], "Edit|Write")
        self.assertEqual(events["PostToolUse"][0]["matcher"], "Edit|Write")

    def test_commands_are_codex_scoped_and_resolve_from_git_root(self):
        self.assertIn("hooks", self.config)
        for groups in self.config["hooks"].values():
            for group in groups:
                for handler in group["hooks"]:
                    command = handler["command"]
                    self.assertIn("NEYRA_HOOK_HOST=codex", command)
                    self.assertIn("git rev-parse --show-toplevel", command)
                    self.assertIn("|| pwd", command)

    def test_installer_explains_codex_hook_trust_step(self):
        installer = (KIT / "install.sh").read_text(encoding="utf-8")
        self.assertIn("/hooks", installer)
        self.assertIn("review and trust", installer.lower())

    def test_validator_accepts_the_published_template(self):
        result = subprocess.run(
            ["python3", str(KIT / "validate-codex-hooks.py"), str(TEMPLATE)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_rejects_the_pre_release_flat_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            stale = pathlib.Path(tmp) / "hooks.json"
            stale.write_text(
                json.dumps(
                    {
                        "SessionStart": [
                            {
                                "command": "NEYRA_HOOK_HOST=codex "
                                "agents/neyra-dev-kit/hooks/session-start.sh"
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(KIT / "validate-codex-hooks.py"), str(stale)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("top-level 'hooks' object", result.stdout + result.stderr)

    def test_doctor_runs_the_codex_config_validator(self):
        doctor = (KIT / "doctor.sh").read_text(encoding="utf-8")
        self.assertIn("validate-codex-hooks.py", doctor)
        self.assertIn("test-codex-hooks.py", doctor)
        self.assertIn(
            r'*** Update File: src/allowed.py\n@@\n-old\n+new\n*** Update File: AGENTS.neyra-devkit.md',
            doctor,
        )

    def test_guard_blocks_any_managed_path_in_multifile_apply_patch(self):
        payload = {
            "tool_input": {
                "command": """*** Begin Patch
*** Update File: src/allowed.py
@@
-old
+new
*** Update File: AGENTS.neyra-devkit.md
@@
-old
+new
*** End Patch
"""
            }
        }
        result = subprocess.run(
            [str(HOOKS / "pre-tool-use-guard.sh")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "NEYRA_HOOK_HOST": "codex"},
        )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("AGENTS.neyra-devkit.md", result.stderr)

    def test_formatter_visits_every_path_in_multifile_apply_patch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "first.py").write_text("x=1\n", encoding="utf-8")
            (root / "second.py").write_text("y=2\n", encoding="utf-8")
            bin_dir = root / "bin"
            bin_dir.mkdir()
            log = root / "ruff.log"
            ruff = bin_dir / "ruff"
            ruff.write_text(
                '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "$NEYRA_RUFF_LOG"\n',
                encoding="utf-8",
            )
            ruff.chmod(0o755)
            payload = {
                "tool_input": {
                    "command": """*** Begin Patch
*** Update File: first.py
@@
-x = 1
+x=1
*** Update File: second.py
@@
-y = 2
+y=2
*** End Patch
"""
                }
            }
            result = subprocess.run(
                [str(HOOKS / "post-tool-use-format.sh")],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                check=False,
                cwd=root,
                env={
                    **os.environ,
                    "NEYRA_HOOK_HOST": "codex",
                    "NEYRA_RUFF_LOG": str(log),
                    "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                },
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                log.read_text(encoding="utf-8").splitlines(),
                ["format first.py", "format second.py"],
            )

    def test_guard_blocks_managed_move_destination(self):
        payload = {
            "tool_input": {
                "command": """*** Begin Patch
*** Update File: src/allowed.py
*** Move to: AGENTS.neyra-devkit.md
@@
-old
+new
*** End Patch
"""
            }
        }
        result = subprocess.run(
            [str(HOOKS / "pre-tool-use-guard.sh")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "NEYRA_HOOK_HOST": "codex"},
        )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("AGENTS.neyra-devkit.md", result.stderr)

    def test_guard_blocks_codex_explicit_file_path(self):
        result = subprocess.run(
            [str(HOOKS / "pre-tool-use-guard.sh")],
            input=json.dumps(
                {"tool_input": {"file_path": "AGENTS.neyra-devkit.md"}}
            ),
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "NEYRA_HOOK_HOST": "codex"},
        )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("AGENTS.neyra-devkit.md", result.stderr)

    def test_guard_denies_cursor_file_path(self):
        result = subprocess.run(
            [str(HOOKS / "pre-tool-use-guard.sh")],
            input=json.dumps({"file_path": "AGENTS.neyra-devkit.md"}),
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "NEYRA_HOOK_HOST": "cursor"},
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(result.stdout, "Cursor guard returned no permission payload")
        self.assertEqual(json.loads(result.stdout)["permission"], "deny")


if __name__ == "__main__":
    unittest.main()
