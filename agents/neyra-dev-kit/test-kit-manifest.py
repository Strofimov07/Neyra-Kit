#!/usr/bin/env python3
"""Integration regression: the shipped-file checksum manifest (NEB-1835 §1).

A consumer on kit 0.38.0 ran a pre-0.36 check_code_node.py for weeks: one copy was
refreshed by the installer, another was not, and nothing compared the installed bundle
with canon at that VERSION. Canon now records the sha256 of every verbatim-shipped file
(KIT_MANIFEST.sha256, generated); a consumer's doctor recomputes them.
Canonical-only (doctor's canonical block); needs git + the source kit.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent.parent
INSTALL = KIT / "install.sh"
CONFIG = KIT / "configs" / "_product.example.sh"
TOOL = KIT / "kit-manifest.py"
MANIFEST = KIT / "KIT_MANIFEST.sha256"


def _install(target):
    return subprocess.run(["bash", str(INSTALL), "product", str(target), str(CONFIG)], capture_output=True, text=True)


def _tool(mode, root):
    return subprocess.run([sys.executable, str(TOOL), mode, str(root)], capture_output=True, text=True)


class KitManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def consumer(self):
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        return Path(self.tmp)

    def test_committed_manifest_is_fresh_and_lists_the_shipped_set(self):
        r = _tool("--check", ROOT)
        self.assertEqual(0, r.returncode, r.stdout)
        text = MANIFEST.read_text(encoding="utf-8")
        for rel in (
            "agents/neyra-dev-kit/hooks/stop-gate.sh",
            "agents/neyra-dev-kit/hooks/lib/host-io.sh",
            "agents/neyra-dev-kit/doctor.sh",
            "agents/neyra-dev-kit/kit-manifest.py",
            "docs/knowledge/check_code_node.py",
            "docs/knowledge/routines/doc-freshness.SKILL.md",
        ):
            self.assertIn(f"  {rel}\n", text, rel)
        for absent in ("agents/neyra-dev-kit/VERSION", "agents/neyra-dev-kit/KIT_MANIFEST.sha256"):
            self.assertNotIn(absent, text)

    def test_check_fails_when_a_shipped_file_changes(self):
        # Work on a copy of the canonical tree so the real manifest is never touched.
        copy = Path(self.tmp, "canon")
        shutil.copytree(ROOT / "agents" / "neyra-dev-kit", copy / "agents" / "neyra-dev-kit",
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.assertEqual(0, _tool("--check", copy).returncode)
        hook = copy / "agents/neyra-dev-kit/hooks/stop-gate.sh"
        hook.write_text(hook.read_text(encoding="utf-8") + "# drift\n", encoding="utf-8")
        r = _tool("--check", copy)
        self.assertEqual(1, r.returncode, r.stdout)
        self.assertIn("changed since --write: agents/neyra-dev-kit/hooks/stop-gate.sh", r.stdout)
        self.assertEqual(0, _tool("--write", copy).returncode)
        self.assertEqual(0, _tool("--check", copy).returncode)

    def test_fresh_install_verifies_clean(self):
        c = self.consumer()
        self.assertTrue((c / "agents/neyra-dev-kit/KIT_MANIFEST.sha256").is_file())
        r = _tool("--verify", c)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn("ok: kit bundle matches canonical", r.stdout)
        self.assertNotIn("WARN", r.stdout)

    def test_modified_hook_fails_verify_and_consumer_doctor(self):
        c = self.consumer()
        hook = c / "agents/neyra-dev-kit/hooks/stop-gate.sh"
        hook.write_text(hook.read_text(encoding="utf-8") + "# local patch\n", encoding="utf-8")
        r = _tool("--verify", c)
        self.assertEqual(1, r.returncode, r.stdout)
        self.assertIn("MODIFIED agents/neyra-dev-kit/hooks/stop-gate.sh", r.stdout)
        d = subprocess.run(["bash", str(c / "agents/neyra-dev-kit/doctor.sh")], capture_output=True, text=True, cwd=c)
        self.assertNotEqual(0, d.returncode)
        self.assertIn("── bundle integrity", d.stdout)
        self.assertIn("MODIFIED agents/neyra-dev-kit/hooks/stop-gate.sh", d.stdout)

    def test_stale_leftover_in_bundle_is_reported_not_failed(self):
        c = self.consumer()
        leftover = c / "agents/neyra-dev-kit/knowledge/check_code_node.py"  # the NEB-1835 shape
        leftover.parent.mkdir(parents=True)
        leftover.write_text("# pre-0.36 copy\n", encoding="utf-8")
        r = _tool("--verify", c)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn("UNMANAGED agents/neyra-dev-kit/knowledge/check_code_node.py", r.stdout)
        self.assertIn("older install", r.stdout)

    def test_partial_upgrade_is_a_version_mismatch(self):
        c = self.consumer()
        (c / ".neyra-dev-kit.version").write_text("0.0.1\n", encoding="utf-8")
        r = _tool("--verify", c)
        self.assertEqual(1, r.returncode, r.stdout)
        self.assertIn("partial upgrade", r.stdout)

    def test_removed_scaffold_only_warns(self):
        c = self.consumer()
        shutil.rmtree(c / "docs" / "knowledge")
        r = _tool("--verify", c)
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn("MISSING  docs/knowledge/check_code_node.py", r.stdout)


if __name__ == "__main__":
    unittest.main()
