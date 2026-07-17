#!/usr/bin/env python3
"""Regression tests for canonical vs consumer skill-mapping checks."""

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
