#!/usr/bin/env python3
"""Regression: handoff file, PreCompact marker, tracker queue, and their session-start injection (NEB-1669).

A consumer lost its tracker for seven days: closures were finished locally, an audit result
went into a free-form note, and the fallback the bootstrap named did not exist on disk, so
the next session never learned of the debt. Now: `.neyra/handoff.md` (stamped by the
PreCompact hook), `.neyra/tracker-queue.jsonl` (replayable), and a SessionStart injection
that reports both until they are empty. Canonical-only; needs git + the source kit.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
HOOKS = KIT / "hooks"
TQ = KIT / "tracker-queue.py"


def tq(root, *args):
    return subprocess.run([sys.executable, str(TQ), *args], capture_output=True, text=True,
                          env={**os.environ, "CLAUDE_PROJECT_DIR": str(root)})


def hook(name, root, payload=None, host="codex"):
    return subprocess.run([str(HOOKS / name)], input=json.dumps(payload or {}), capture_output=True, text=True,
                          env={**os.environ, "CLAUDE_PROJECT_DIR": str(root), "NEYRA_HOOK_HOST": host})


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp)
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pre_compact_creates_skeleton_then_only_stamps(self):
        r = hook("pre-compact.sh", self.root, {"trigger": "auto"})
        self.assertEqual(0, r.returncode, r.stderr)
        h = (self.root / ".neyra" / "handoff.md").read_text(encoding="utf-8")
        for section in ("## Completed this session", "## In progress", "## Blockers", "## Decisions made",
                        "## Context to load first", "## Pending tracker mutations"):
            self.assertIn(section, h)
        self.assertEqual(1, h.count("**[compaction (auto)"))
        r = hook("pre-compact.sh", self.root, {"trigger": "manual"})
        self.assertEqual(0, r.returncode, r.stderr)
        h2 = (self.root / ".neyra" / "handoff.md").read_text(encoding="utf-8")
        self.assertEqual(1, h2.count("## Completed this session"))  # skeleton not duplicated
        self.assertEqual(1, h2.count("**[compaction (manual)"))
        metrics = (self.root / ".neyra" / "kit-metrics.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event":"compact"', metrics)

    def test_tracker_queue_round_trip(self):
        self.assertEqual("", tq(self.root, "status").stdout)
        r = tq(self.root, "add", "--op", "state", "--issue", "NEB-1", "--state", "Done", "--text", "closing note",
               "--reason", "Linear returned HTML")
        self.assertEqual(0, r.returncode, r.stderr)
        r = tq(self.root, "add", "--op", "comment", "--issue", "NEB-2", "--text", "audit result")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(1, tq(self.root, "add", "--op", "state", "--issue", "NEB-3").returncode)  # --state missing
        st = tq(self.root, "status").stdout
        self.assertIn("2 queued tracker mutation(s)", st)
        ls = tq(self.root, "list").stdout
        self.assertIn("NEB-1 → Done", ls)
        self.assertIn("Linear returned HTML", ls)
        self.assertIn("audit result", ls)
        self.assertEqual(0, tq(self.root, "done", "1").returncode)
        self.assertIn("1 queued", tq(self.root, "status").stdout)
        self.assertEqual(0, tq(self.root, "done", "--all").returncode)
        self.assertEqual("", tq(self.root, "status").stdout)
        done = (self.root / ".neyra" / "tracker-queue.done.jsonl").read_text(encoding="utf-8")
        self.assertEqual(2, done.count('"done_at"'))

    def test_session_start_injects_handoff_and_debt(self):
        (self.root / ".neyra").mkdir()
        (self.root / ".neyra" / "handoff.md").write_text("## In progress (exact next step)\n- finish the export\n", encoding="utf-8")
        tq(self.root, "add", "--op", "comment", "--issue", "NEB-9", "--text", "queued while down")
        (self.root / ".neyra" / "kit-evolution-pending.log").write_text("2026-09-01 | a signal | route:x | pattern\n", encoding="utf-8")
        r = hook("session-start.sh", self.root)
        self.assertEqual(0, r.returncode, r.stderr)
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("## Handoff from the previous session", ctx)
        self.assertIn("finish the export", ctx)
        self.assertIn("## Tracker debt — replay before new work", ctx)
        self.assertIn("1 queued tracker mutation(s)", ctx)
        self.assertIn("1 pending kit-evolution signal(s)", ctx)

    def test_session_start_is_silent_when_nothing_is_open(self):
        r = hook("session-start.sh", self.root)
        self.assertEqual(0, r.returncode, r.stderr)
        ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("Handoff from the previous session", ctx)
        self.assertNotIn("Tracker debt", ctx)

    def test_install_wires_pre_compact_and_ignores_neyra(self):
        r = subprocess.run(["bash", str(KIT / "install.sh"), "product", self.tmp, str(KIT / "configs" / "_product.example.sh")],
                           capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stderr)
        settings = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        cmds = [h["command"] for g in settings["hooks"].get("PreCompact", []) for h in g["hooks"]]
        self.assertTrue(any("pre-compact.sh" in c for c in cmds), settings["hooks"].keys())
        self.assertIn(".neyra/", (self.root / ".gitignore").read_text(encoding="utf-8").splitlines())
        self.assertTrue((self.root / "agents/neyra-dev-kit/tracker-queue.py").is_file())
        self.assertTrue((self.root / "agents/neyra-dev-kit/hooks/pre-compact.sh").is_file())


if __name__ == "__main__":
    unittest.main()
