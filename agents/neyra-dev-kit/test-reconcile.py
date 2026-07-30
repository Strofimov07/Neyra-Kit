#!/usr/bin/env python3
"""Integration regression: install.sh reconciles kit-owned blocks on upgrade (NEB-1648, NEB-1651).

The inline AGENTS.md block and the .claude/settings.json hook wiring must be refreshed on a
re-install (upgrade), not skipped-if-present, while the consumer's own content is preserved.
Canonical-only (invoked from doctor's canonical block); needs git + jq + the source kit.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
INSTALL = KIT / "install.sh"
CONFIG = KIT / "configs" / "_product.example.sh"


def _install(target, *flags):
    return subprocess.run(
        ["bash", str(INSTALL), *flags, "product", str(target), str(CONFIG)],
        capture_output=True,
        text=True,
    )


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_reconcile_block_and_hooks_on_upgrade(self):
        agents = Path(self.tmp, "AGENTS.md")
        agents.write_text("# Repo\n\nRepo-owned line.\n", encoding="utf-8")
        self.assertEqual(0, (r := _install(self.tmp)).returncode, r.stderr)
        settings = Path(self.tmp, ".claude/settings.json")
        self.assertIn("neyra-dev-kit:begin", agents.read_text())
        self.assertIn("## Current lessons", agents.read_text())
        self.assertIn("Task|Workflow", settings.read_text())

        # Drift: rename a managed section, stale the kit matcher, add a consumer-owned hook.
        agents.write_text(
            agents.read_text().replace("## Current lessons", "## OLD lessons"), encoding="utf-8"
        )
        s = json.loads(settings.read_text())
        for grp in s["hooks"]["PreToolUse"]:
            if "count-task" in grp["hooks"][0]["command"]:
                grp["matcher"] = "Task"
        s["hooks"]["PreToolUse"].append(
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo consumer-own"}]}
        )
        settings.write_text(json.dumps(s), encoding="utf-8")

        self.assertEqual(0, (r := _install(self.tmp)).returncode, r.stderr)
        at, st = agents.read_text(), settings.read_text()
        self.assertIn("## Current lessons", at, "reconcile must restore the drifted managed section")
        self.assertNotIn("OLD lessons", at)
        self.assertEqual(1, at.count("neyra-dev-kit:begin"), "markers must not duplicate")
        self.assertIn("Repo-owned line.", at, "repo content outside the block must be kept")
        self.assertIn("Task|Workflow", st, "stale kit matcher must be refreshed on upgrade")
        self.assertIn("consumer-own", st, "consumer-owned hook must be preserved")

    def test_migrate_unmarked_legacy_block(self):
        agents = Path(self.tmp, "AGENTS.md")
        agents.write_text(
            "# Repo\n\nMine.\n\n## Engineering process (neyra-dev-kit)\n\nOLD v0.25 content only.\n",
            encoding="utf-8",
        )
        self.assertEqual(0, (r := _install(self.tmp)).returncode, r.stderr)
        at = agents.read_text()
        self.assertIn("neyra-dev-kit:begin", at, "unmarked legacy block must migrate to markers")
        self.assertNotIn("OLD v0.25", at, "legacy content must be replaced")
        self.assertIn("Mine.", at, "repo content before the block must be kept")
        self.assertIn("## Current lessons", at)


if __name__ == "__main__":
    unittest.main()
