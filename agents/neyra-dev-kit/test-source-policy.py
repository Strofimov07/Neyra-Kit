#!/usr/bin/env python3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


KIT = Path(__file__).resolve().parent
ROOT = KIT.parents[1]
POLICY = KIT / "source-policy.py"
CANONICAL_REMOTE = "git@github.com:Strofimov07/Neyra-Kit.git"


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def run_policy(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(POLICY), "--root", str(root), *args],
        capture_output=True,
        text=True,
    )


class CanonicalSourcePolicyTests(unittest.TestCase):
    def make_repo(self, remote: str, marker: bool) -> tempfile.TemporaryDirectory[str]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        git(root, "init", "-q")
        git(root, "remote", "add", "origin", remote)
        if marker:
            (root / ".neyra-kit-canonical").write_text(
                f"repository={CANONICAL_REMOTE}\n", encoding="utf-8"
            )
        return tmp

    def test_real_repository_is_the_canonical_authoring_source(self):
        result = run_policy(ROOT, "--require-canonical")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("canonical", result.stdout)

    def test_consumer_repository_cannot_author_shared_kit_changes(self):
        with self.make_repo("git@github.com:Strofimov07/AIBrowser.git", False) as tmp:
            result = run_policy(Path(tmp), "--require-canonical")
        self.assertEqual(2, result.returncode)
        self.assertIn("consumer", result.stderr)
        self.assertIn("Neyra-Kit", result.stderr)

    def test_marker_cannot_forge_canonical_status_on_another_remote(self):
        with self.make_repo("git@github.com:Strofimov07/AIBrowser.git", True) as tmp:
            result = run_policy(Path(tmp), "--require-canonical")
        self.assertEqual(2, result.returncode)
        self.assertIn("origin", result.stderr)

    def test_legacy_publisher_fails_closed(self):
        result = subprocess.run(
            ["bash", str(KIT / "publish.sh")], capture_output=True, text=True
        )
        self.assertEqual(2, result.returncode)
        message = result.stdout + result.stderr
        self.assertIn("retired", message.lower())
        self.assertIn("Neyra-Kit", message)

    def test_authoring_docs_do_not_route_changes_through_a_product_monorepo(self):
        files = [
            ROOT / "README.md",
            ROOT / "README.ru.md",
            KIT / "EVOLVING-THE-KIT.md",
            KIT / "KIT_BOOTSTRAP.md",
            KIT / "kit-metrics.py",
            ROOT / "agents/dev-skills/kit-evolution/SKILL.md",
            ROOT / ".claude/agents/kit-evolution.md",
            ROOT / ".claude/agents/kit-onboarding.md",
            KIT / "README.md",
            KIT / "manifest.yml",
        ]
        stale_phrases = (
            "monorepo is the canon",
            "monorepo stays canon",
            "publish to the external kit repo",
            "run publish.sh",
            "published artifact",
            "публикуемый артефакт",
            "this monorepo",
        )
        for path in files:
            content = path.read_text(encoding="utf-8").lower()
            for phrase in stale_phrases:
                self.assertNotIn(phrase.lower(), content, f"{path}: {phrase}")
        self.assertFalse((KIT / "templates/EXTERNAL_README.en.md").exists())
        self.assertFalse((KIT / "templates/EXTERNAL_README.ru.md").exists())

    def test_canonical_history_and_signal_ledgers_exist(self):
        self.assertTrue((KIT / "decisionLog.md").is_file())
        self.assertTrue((KIT / "signals.log").is_file())

    def test_installer_has_no_product_monorepo_dependency(self):
        installer = (KIT / "install.sh").read_text(encoding="utf-8")
        manifest = (KIT / "manifest.yml").read_text(encoding="utf-8")
        self.assertNotIn("MONOREPO", installer)
        self.assertNotIn("plugins/neyra-cursor-plugin", installer)
        self.assertNotIn("plugins/neyra-cursor-plugin", manifest)

    def test_canonical_mapping_check_never_relaxes_to_consumer_mode(self):
        result = subprocess.run(
            [sys.executable, str(KIT / "check-skill-mapping.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("consumer mode", result.stdout)

    def test_installer_stamps_consumers_with_the_canonical_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            git(target, "init", "-q")
            result = subprocess.run(
                [
                    "bash",
                    str(KIT / "install.sh"),
                    "product",
                    str(target),
                    str(KIT / "configs/_product.example.sh"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            stamp = (target / ".neyra-dev-kit.source").read_text(encoding="utf-8")
            self.assertIn(CANONICAL_REMOTE, stamp)
            self.assertFalse((target / ".neyra-kit-canonical").exists())


if __name__ == "__main__":
    unittest.main()
