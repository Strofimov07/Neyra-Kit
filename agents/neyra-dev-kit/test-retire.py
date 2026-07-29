#!/usr/bin/env python3
"""Integration regression for the installer's retirement pass (NEB-1487).

Installs the real kit into a temp git repo, then simulates a file the current kit no
longer manages (recorded in the prior manifest) and re-installs, asserting RET-1..5:
  RET-1 an unmodified stale kit file is removed;
  RET-2 a stale file changed since install (checksum mismatch) is KEPT;
  RET-3 --dry-run removes nothing;
  RET-5 a path absent from the manifest is never touched.
Canonical-only (invoked from doctor's canonical block); needs git + the source kit.
"""
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
INSTALL = KIT / "install.sh"
CONFIG = KIT / "configs" / "_product.example.sh"
MANIFEST_REL = ".neyra/kit-manifest.tsv"


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _install(target, *flags):
    return subprocess.run(
        ["bash", str(INSTALL), *flags, "product", str(target), str(CONFIG)],
        capture_output=True,
        text=True,
    )


class RetireTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True, capture_output=True)
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        self.mf = Path(self.tmp, MANIFEST_REL)
        self.assertTrue(self.mf.is_file(), "install did not record the manifest")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _seed(self, relpath, content, manifest_sha):
        p = Path(self.tmp, relpath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        if manifest_sha is not None:
            with open(self.mf, "a", encoding="utf-8") as fh:
                fh.write("%s\t%s\n" % (manifest_sha, relpath))
        return p

    def test_ret1_ret2_ret5_on_reinstall(self):
        # RET-1: recorded with its true checksum → unmodified kit file → must be removed.
        old = self._seed("agents/neyra-dev-kit/OLD_ARTIFACT.md", "stale\n", None)
        with open(self.mf, "a", encoding="utf-8") as fh:
            fh.write("%s\t%s\n" % (_sha(old), "agents/neyra-dev-kit/OLD_ARTIFACT.md"))
        # RET-2: recorded with a WRONG checksum → looks user-modified → must be kept.
        edited = self._seed("agents/neyra-dev-kit/USER_EDITED.md", "edited\n", "0" * 64)
        # RET-5: never recorded in the manifest → must never be touched.
        unmanaged = self._seed("agents/neyra-dev-kit/NOT_IN_MANIFEST.md", "keep\n", None)

        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertFalse(old.exists(), "RET-1: unmodified stale kit file should be retired")
        self.assertTrue(edited.exists(), "RET-2: checksum-mismatch file must be kept")
        self.assertTrue(unmanaged.exists(), "RET-5: a path absent from the manifest must not be touched")

    def test_ret3_dry_run_removes_nothing(self):
        p = self._seed("agents/neyra-dev-kit/OLD_DRY.md", "stale\n", None)
        with open(self.mf, "a", encoding="utf-8") as fh:
            fh.write("%s\t%s\n" % (_sha(p), "agents/neyra-dev-kit/OLD_DRY.md"))
        r = _install(self.tmp, "--dry-run")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue(p.exists(), "RET-3: --dry-run must not remove anything")


if __name__ == "__main__":
    unittest.main()
