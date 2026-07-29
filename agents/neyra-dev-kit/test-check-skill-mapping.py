#!/usr/bin/env python3
"""Regression tests for canonical vs consumer skill-mapping checks."""

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check-skill-mapping.py")
SPEC = importlib.util.spec_from_file_location("check_skill_mapping", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SkillMappingModeTests(unittest.TestCase):
    def test_consumer_without_mapping_table_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_dir = root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)

            self.assertEqual(
                MODULE.check_agents_table(
                    str(root), {"implementation-loop"}, str(agents_dir), True
                ),
                [],
            )

    def test_canonical_repo_without_mapping_table_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_dir = root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)

            errors = MODULE.check_agents_table(
                str(root), {"implementation-loop"}, str(agents_dir), False
            )

            self.assertEqual(len(errors), 1)
            self.assertIn("mapping table", errors[0])


class ProfileAwareTests(unittest.TestCase):
    """NEB-1484: main() is profile-aware — a non-dev bundle (no agents/dev-skills but
    another skills layer present) is N/A, not a failure; only a total absence of any
    skills layer fails closed."""

    def _main_with_root(self, root):
        orig = MODULE._repo_root
        MODULE._repo_root = lambda: str(root)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                return MODULE.main()
        finally:
            MODULE._repo_root = orig

    def test_non_dev_bundle_is_na_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "agents" / "mgmt-skills" / "team-health-check"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: team-health-check\n---\n", encoding="utf-8")
            (root / ".claude" / "agents").mkdir(parents=True)
            self.assertEqual(0, self._main_with_root(root))

    def test_no_skill_layer_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".claude" / "agents").mkdir(parents=True)  # no skills layer at all
            self.assertEqual(1, self._main_with_root(root))


if __name__ == "__main__":
    unittest.main()
