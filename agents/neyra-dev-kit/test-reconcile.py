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
        self.assertIn("## Self-Improvement Rule", agents.read_text())
        self.assertIn("Task|Workflow", settings.read_text())

        # Drift: rename a managed section, stale the kit matcher, add a consumer-owned hook.
        agents.write_text(
            agents.read_text().replace("## Self-Improvement Rule", "## OLD rule"), encoding="utf-8"
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
        self.assertIn(
            "## Self-Improvement Rule", at, "reconcile must restore the drifted managed section"
        )
        self.assertNotIn("OLD rule", at)
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
        self.assertIn("## Self-Improvement Rule", at)


class LessonsTests(unittest.TestCase):
    """NEB-1662: project-specific lessons are consumer data — settings/, never the managed block.

    The managed block is regenerated on every install, so a lessons section inside it is
    either wiped on upgrade or duplicated by a repo-owned copy outside it. Lessons live in
    settings/lessons.md, which the installer seeds once and then never touches.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_block_carries_no_lessons_section(self):
        agents = Path(self.tmp, "AGENTS.md")
        agents.write_text("# Repo\n", encoding="utf-8")
        self.assertEqual(0, (r := _install(self.tmp)).returncode, r.stderr)
        self.assertNotIn(
            "## Current lessons",
            agents.read_text(),
            "the regenerated block must not own consumer lesson data",
        )

    def test_seeds_lessons_file_once_and_never_overwrites(self):
        Path(self.tmp, "AGENTS.md").write_text("# Repo\n", encoding="utf-8")
        self.assertEqual(0, (r := _install(self.tmp)).returncode, r.stderr)
        lessons = Path(self.tmp, "settings/lessons.md")
        self.assertTrue(lessons.is_file(), "installer must seed settings/lessons.md")

        lessons.write_text(
            lessons.read_text() + "\n- A promoted project lesson.\n", encoding="utf-8"
        )
        self.assertEqual(0, (r := _install(self.tmp)).returncode, r.stderr)
        self.assertIn(
            "A promoted project lesson.",
            lessons.read_text(),
            "an upgrade must never clobber accumulated lessons",
        )

    def test_flags_a_legacy_lessons_section_for_migration(self):
        agents = Path(self.tmp, "AGENTS.md")
        agents.write_text(
            "# Repo\n\n## Current lessons\n\n- Legacy lesson kept by the repo.\n", encoding="utf-8"
        )
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn(
            "settings/lessons.md",
            r.stdout,
            "a consumer still holding lessons in AGENTS.md must be told where they now live",
        )
        self.assertIn(
            "Legacy lesson kept by the repo.",
            agents.read_text(),
            "never delete repo-owned lesson content — report, don't fix",
        )


if __name__ == "__main__":
    unittest.main()
