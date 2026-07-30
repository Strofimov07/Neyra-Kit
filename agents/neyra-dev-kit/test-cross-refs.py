#!/usr/bin/env python3
"""Regression for check-cross-refs.py (NEB-1591): a dead AGENTS.md section anchor is
detected; a resolving one is not."""
import contextlib
import importlib.util
import io
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


class ConsumerUnionTests(unittest.TestCase):
    """NEB-1647: in a consumer, anchors resolve against the union of AGENTS.md / CLAUDE.md /
    AGENTS.neyra-devkit.md — the kit block lives in AGENTS.md, not the render — so a section
    present in AGENTS.md must not false-WARN. A section absent from all three still WARNs."""

    def _run(self, root):
        orig = MOD._repo_root
        MOD._repo_root = lambda: str(root)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = MOD.main()
        finally:
            MOD._repo_root = orig
        return rc, buf.getvalue()

    def _consumer(self, tmp, agents_md_body):
        root = Path(tmp)
        (root / ".neyra-dev-kit.source").write_text("repository=x\n", encoding="utf-8")
        sk = root / "agents" / "dev-skills" / "kit-evolution"
        sk.mkdir(parents=True)
        (sk / "SKILL.md").write_text(
            "This operationalizes the `Self-Improvement Rule` in AGENTS.md.\n", encoding="utf-8"
        )
        (root / "AGENTS.md").write_text(agents_md_body, encoding="utf-8")
        return root

    def test_consumer_resolves_section_in_agents_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._consumer(tmp, "# Repo\n\n## Self-Improvement Rule\n\nbody\n")
            rc, out = self._run(root)
            self.assertEqual(0, rc)
            self.assertIn("resolve", out)
            self.assertNotIn("dead AGENTS.md", out)

    def test_consumer_warns_when_section_absent_everywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._consumer(tmp, "# Repo\n\nno kit sections here\n")
            rc, out = self._run(root)
            self.assertEqual(0, rc)  # consumer is warn-only, never fails
            self.assertIn("dead AGENTS.md", out)  # but still WARNs — not evergreen


if __name__ == "__main__":
    unittest.main()
