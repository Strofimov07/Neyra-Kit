#!/usr/bin/env python3
"""Regression for check_code_node.py review notes (NEB-1835).

1. An explicit KNOWLEDGE_DIFF_BASE that does not resolve fails loudly instead of degrading
   to the guessed branch list.
2. A missing knowledge-map reads as "the check did not run", never as "no mapped paths
   touched"; under --strict it is a non-zero exit.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
SCRIPT = KIT / "knowledge" / "check_code_node.py"


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class CodeNodeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _git(self.tmp, "init", "-q")
        _git(self.tmp, "config", "user.email", "t@example.invalid")
        _git(self.tmp, "config", "user.name", "t")
        Path(self.tmp, "a.txt").write_text("a\n", encoding="utf-8")
        _git(self.tmp, "add", "a.txt")
        _git(self.tmp, "commit", "-q", "-m", "base")
        # A consumer copy of the script next to its (absent) map, as install.sh stages it.
        self.kdir = Path(self.tmp, "docs", "knowledge")
        self.kdir.mkdir(parents=True)
        shutil.copy(SCRIPT, self.kdir / "check_code_node.py")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_script(self, *args, env=None):
        return subprocess.run(
            [sys.executable, str(self.kdir / "check_code_node.py"), *args],
            cwd=self.tmp, capture_output=True, text=True, env={**os.environ, **(env or {})},
        )

    def test_explicit_unresolvable_base_fails_loudly(self):
        r = self.run_script(env={"KNOWLEDGE_DIFF_BASE": "no-such-branch"})
        self.assertNotEqual(0, r.returncode, r.stdout)
        self.assertIn("KNOWLEDGE_DIFF_BASE", r.stderr)
        self.assertNotIn("no mapped paths touched", r.stdout)

    def test_missing_map_is_not_a_no_op(self):
        r = self.run_script("HEAD")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("did not run", r.stdout)
        self.assertNotIn("no mapped paths touched", r.stdout)
        r = self.run_script("HEAD", "--strict")
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)

    def test_present_map_still_reports_no_hits(self):
        (self.kdir / "knowledge-map.yml").write_text(
            "code_to_node:\n  - paths: ['src/**']\n    nodes: ['Node']\n", encoding="utf-8"
        )
        r = self.run_script("HEAD")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("no mapped paths touched", r.stdout)


if __name__ == "__main__":
    unittest.main()
