#!/usr/bin/env python3
"""Regression for check-cross-refs.py (NEB-1591): a dead AGENTS.md section anchor is
detected; a resolving one is not."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-cross-refs.py")
SPEC = importlib.util.spec_from_file_location("check_cross_refs", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class CrossRefTests(unittest.TestCase):
    def test_dead_anchor_detected_live_anchor_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "agents" / "dev-skills"
            (skills / "live").mkdir(parents=True)
            (skills / "live" / "SKILL.md").write_text(
                "This operationalizes the `Self-Improvement Rule` in AGENTS.md.",
                encoding="utf-8",
            )
            (skills / "dead").mkdir(parents=True)
            (skills / "dead" / "SKILL.md").write_text(
                "Route to canonical Neyra-Kit: AGENTS.md `Nonexistent Section`.",
                encoding="utf-8",
            )
            headings = {"Self-Improvement Rule", "Current lessons"}
            refs = MOD.scan_skill_refs(str(skills))
            unresolved = [(d, n) for (d, n) in refs if n not in headings]

            self.assertIn(("dead", "Nonexistent Section"), unresolved)
            self.assertFalse(
                [d for d, _ in unresolved if d == "live"],
                "a section present in the headings must not be flagged",
            )

    def test_headings_parse(self):
        heads = MOD.headings_of("# Title\n\n## Self-Improvement Rule\n\n### Current lessons\n")
        self.assertIn("Self-Improvement Rule", heads)
        self.assertIn("Current lessons", heads)


if __name__ == "__main__":
    unittest.main()
