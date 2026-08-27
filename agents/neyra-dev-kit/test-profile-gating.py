#!/usr/bin/env python3
"""Integration regression: settings/product.yml selects the installed subagent set (v0.41.0).

v0.40.0 shipped a profile that only *reported* which gates applied — every agent was
installed regardless, so a declaration changed nothing an agent would ever notice.
install.sh now consumes `product-profile.py --skip-agents`. These tests pin the two
things that make that safe:

  PG-1 absence is not "false" — no profile, or a profile that predates a flag, installs
       everything (the pre-v0.41.0 behaviour every existing consumer already has);
  PG-2 flipping a flag off removes an UNMODIFIED copy but keeps an edited one, the same
       policy the retirement pass uses for kit files.

Canonical-only (invoked from doctor's canonical block); needs git + the source kit.
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
INSTALL = KIT / "install.sh"
PROFILE = KIT / "product-profile.py"
CONFIG = KIT / "configs" / "_product.example.sh"

CONDITIONAL = ["grounding-gate", "eval-baseline", "retrieval-review",
               "llm-cost-guard", "data-inventory", "long-job-discipline"]
# Predates the launch layer: must be installed whatever the profile says.
UNCONDITIONAL = "incident-runbook"


def _install(target, *flags):
    return subprocess.run(
        ["bash", str(INSTALL), *flags, "dev", str(target), str(CONFIG)],
        capture_output=True, text=True,
    )


def _seed_profile(target, **flags):
    seed = subprocess.run(["python3", str(PROFILE), "--seed"],
                          capture_output=True, text=True, check=True).stdout
    for key, val in flags.items():
        old = "%s: false" % key
        assert seed.count(old) == 1, "seed template has no flag %r" % key
        seed = seed.replace(old, "%s: %s" % (key, "true" if val else "false"), 1)
    p = Path(target, "settings")
    p.mkdir(parents=True, exist_ok=True)
    (p / "product.yml").write_text(seed, encoding="utf-8")


def _agent(target, name):
    return Path(target, ".claude", "agents", "%s.md" % name)


class ProfileGatingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pg1_no_profile_installs_everything(self):
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        for a in CONDITIONAL + [UNCONDITIONAL]:
            self.assertTrue(_agent(self.tmp, a).is_file(),
                            "no profile must install %s (pre-v0.41.0 behaviour)" % a)

    def test_pg1_absent_flag_is_not_false(self):
        Path(self.tmp, "settings").mkdir(parents=True, exist_ok=True)
        # A profile written before these flags existed.
        Path(self.tmp, "settings", "product.yml").write_text("name: legacy\nsells: false\n",
                                                             encoding="utf-8")
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        for a in CONDITIONAL:
            self.assertTrue(_agent(self.tmp, a).is_file(),
                            "a flag the profile never mentions must not uninstall %s" % a)

    def test_all_false_installs_none_of_the_conditional_layer(self):
        _seed_profile(self.tmp)
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        for a in CONDITIONAL:
            self.assertFalse(_agent(self.tmp, a).is_file(),
                             "%s is out of scope for this profile and must not be installed" % a)
        self.assertTrue(_agent(self.tmp, UNCONDITIONAL).is_file(),
                        "%s predates the launch layer and stays unconditional" % UNCONDITIONAL)

    def test_a_true_flag_installs_its_agents_only(self):
        _seed_profile(self.tmp, generates_claims=True)
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue(_agent(self.tmp, "grounding-gate").is_file())
        self.assertTrue(_agent(self.tmp, "eval-baseline").is_file())
        self.assertFalse(_agent(self.tmp, "retrieval-review").is_file())

    def test_pg2_flag_flipped_off_removes_pristine_keeps_edited(self):
        _seed_profile(self.tmp, generates_claims=True, retrieval=True)
        self.assertEqual(0, _install(self.tmp).returncode)
        pristine, edited = _agent(self.tmp, "grounding-gate"), _agent(self.tmp, "retrieval-review")
        self.assertTrue(pristine.is_file() and edited.is_file())
        edited.write_text(edited.read_text(encoding="utf-8") + "\nlocal note\n", encoding="utf-8")

        _seed_profile(self.tmp)  # both flags back to false
        r = _install(self.tmp)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertFalse(pristine.is_file(), "an unmodified out-of-scope agent must be removed")
        self.assertTrue(edited.is_file(), "a locally edited agent must be kept, never deleted")
        self.assertIn("kept retrieval-review", r.stdout)

    def test_deselection_keeps_the_consumer_mapping_check_green(self):
        """The mapping table lists every row; a deselected agent is absent by design.

        Found by installing for real: without this, switching a flag off made the
        consumer's own doctor fail on "AGENTS table maps X but .claude/agents/X.md is
        missing" — a repo that followed the instructions would land on a red doctor.
        """
        _seed_profile(self.tmp, generates_claims=True)
        self.assertEqual(0, _install(self.tmp).returncode)
        r = subprocess.run(["python3", str(Path(self.tmp, "agents/neyra-dev-kit/check-skill-mapping.py"))],
                           capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("out of scope", r.stdout)

    def test_pg2_dry_run_removes_nothing(self):
        _seed_profile(self.tmp, generates_claims=True)
        self.assertEqual(0, _install(self.tmp).returncode)
        a = _agent(self.tmp, "grounding-gate")
        _seed_profile(self.tmp)
        r = _install(self.tmp, "--dry-run")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue(a.is_file(), "--dry-run must not remove an agent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
