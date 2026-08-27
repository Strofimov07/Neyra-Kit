#!/usr/bin/env python3
"""Regression: an optional installed artifact can be declined, and the decision sticks.

install.sh scaffolds `.github/workflows/doc-freshness.yml` when it is absent. "Absent"
cannot distinguish "not yet installed" from "deleted on purpose", so a consumer that
removed it (CI cost, a different freshness mechanism) got it back on every upgrade —
with a `paths: ['**']` trigger, i.e. a job on every PR it had deliberately dropped.

ENABLE_DOC_FRESHNESS_WORKFLOW moves that decision into the config, where it survives
upgrades. Switching it off retires an unmodified copy and keeps an edited one — the
same policy the retirement and profile-gating passes already use.

Canonical-only; needs git + the source kit.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
INSTALL = KIT / "install.sh"
BASE_CONFIG = KIT / "configs" / "_product.example.sh"
TEMPLATE = KIT / "knowledge" / "templates" / "doc-freshness.yml"
WF = ".github/workflows/doc-freshness.yml"


def _repo():
    d = Path(tempfile.mkdtemp())
    subprocess.run(["git", "-C", str(d), "init", "-q"], check=True)
    return d


def _config(enabled=None):
    cfg = Path(tempfile.mkdtemp()) / "config.sh"
    text = BASE_CONFIG.read_text()
    if enabled is not None:
        text += "\nENABLE_DOC_FRESHNESS_WORKFLOW=%s\n" % enabled
    cfg.write_text(text)
    return cfg


def _install(target, cfg):
    return subprocess.run(["bash", str(INSTALL), "dev", str(target), str(cfg)],
                          capture_output=True, text=True)


class OptionalArtifacts(unittest.TestCase):
    def test_installed_by_default(self):
        t = _repo()
        _install(t, _config())
        self.assertTrue((t / WF).is_file(), "default install should scaffold the workflow")

    def test_not_installed_when_declined(self):
        t = _repo()
        _install(t, _config(0))
        self.assertFalse((t / WF).is_file(), "ENABLE_DOC_FRESHNESS_WORKFLOW=0 must not scaffold it")

    def test_declining_retires_an_unmodified_copy(self):
        t = _repo()
        _install(t, _config(1))
        self.assertTrue((t / WF).is_file())
        r = _install(t, _config(0))
        self.assertFalse((t / WF).is_file(), "an untouched copy should be retired when declined")
        self.assertIn("removed the unmodified copy", r.stdout + r.stderr)

    def test_declining_keeps_an_edited_copy(self):
        t = _repo()
        _install(t, _config(1))
        (t / WF).write_text(TEMPLATE.read_text() + "\n# local edit\n")
        r = _install(t, _config(0))
        self.assertTrue((t / WF).is_file(), "an edited copy must never be deleted")
        self.assertIn("was edited", r.stdout + r.stderr)

    def test_declining_is_idempotent_when_absent(self):
        t = _repo()
        r = _install(t, _config(0))
        self.assertEqual(r.returncode, 0)
        self.assertFalse((t / WF).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
