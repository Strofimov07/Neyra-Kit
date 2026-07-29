#!/usr/bin/env python3
"""Regression: standalone gates resolve the repo root and fail closed (NEB-1486).

Before this, lint-scope.py / lint-skills.py / check-skill-mapping.py resolved their
targets from the cwd, so running them the way EVOLVING-THE-KIT documents — from
agents/neyra-dev-kit/ — left every default dir unresolved and they printed
"skip … / OK", passing vacuously. The fix resolves the repo root from each script's
own file location and fails closed when no skill layer is found.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
GATES = ["lint-scope.py", "lint-skills.py", "check-skill-mapping.py"]


def _run(script, cwd):
    return subprocess.run(
        [sys.executable, str(KIT / script)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


class GateRootResolution(unittest.TestCase):
    def test_validates_from_kit_dir_not_repo_root(self):
        """The documented EVOLVING-THE-KIT working directory must resolve the repo root
        and exit 0 — not silently no-op from an unresolved cwd. (A non-dev bundle may
        legitimately print "skip" for skill layers it doesn't ship, so exit code — not
        the absence of "skip" — is the signal; the fail-closed case guards vacuous pass.)"""
        for g in GATES:
            r = _run(g, cwd=KIT)
            self.assertEqual(0, r.returncode, "%s:\n%s%s" % (g, r.stdout, r.stderr))

    def test_validates_from_arbitrary_cwd(self):
        """A no-arg run from any unrelated cwd still resolves the real repo root."""
        with tempfile.TemporaryDirectory() as tmp:
            for g in GATES:
                r = _run(g, cwd=tmp)
                self.assertEqual(0, r.returncode, "%s:\n%s%s" % (g, r.stdout, r.stderr))

    def test_fail_closed_when_no_skill_layer(self):
        """A gate copied outside any kit tree, run from an empty cwd, must fail closed
        (exit != 0) instead of printing OK. lint-scope is the representative."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "x" / "y" / "z"
            nested.mkdir(parents=True)
            shutil.copy(KIT / "lint-scope.py", nested / "lint-scope.py")
            r = subprocess.run(
                [sys.executable, str(nested / "lint-scope.py")],
                cwd=str(nested),
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, r.returncode, r.stdout + r.stderr)
            self.assertIn("vacuously", r.stdout)


if __name__ == "__main__":
    unittest.main()
