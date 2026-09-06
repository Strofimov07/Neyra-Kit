#!/usr/bin/env python3
"""Integration regression: install.sh renders reproducible, placeholder-free consumer files.

NEB-1799: an unset MCP prefix must not survive into a generated agent as a literal
{{X_MCP_PREFIX}}__tool — the dependent `tools:` entries are dropped, the line stays
well-formed, and a consumer's doctor fails on any placeholder that does leak.
NEB-2013: the staged doc-freshness routine spec names no machine path, so two installs
on two machines produce byte-identical, trackable files.
Canonical-only (doctor's canonical block); needs git + jq + the source kit.
"""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
INSTALL = KIT / "install.sh"
CONFIG = KIT / "configs" / "_product.example.sh"
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")
AGENT = ".claude/agents/solution-designer.md"  # carries NOTION + FIGMA placeholders in canon
ROUTINE = "docs/knowledge/routines/doc-freshness.SKILL.md"


def _install(target, config=CONFIG):
    return subprocess.run(
        ["bash", str(INSTALL), "product", str(target), str(config)], capture_output=True, text=True
    )


def _tools_line(path):
    lines = [l for l in Path(path).read_text(encoding="utf-8").splitlines() if l.startswith("tools:")]
    return lines[0] if lines else None


class InstallRenderTests(unittest.TestCase):
    def setUp(self):
        self.dirs = []

    def tearDown(self):
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def repo(self):
        d = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=d, check=True, capture_output=True)
        self.dirs.append(d)
        return d

    def test_unset_prefixes_drop_their_entries_and_leave_no_placeholder(self):
        t = self.repo()
        r = _install(t)
        self.assertEqual(0, r.returncode, r.stderr)
        agents = list(Path(t, ".claude/agents").glob("*.md"))
        self.assertTrue(agents)
        for a in agents:
            self.assertIsNone(PLACEHOLDER.search(a.read_text(encoding="utf-8")), a.name)
        self.assertEqual("tools: Read, Grep, Glob", _tools_line(Path(t, AGENT)))

    def test_set_prefix_is_substituted_and_unset_sibling_dropped(self):
        t = self.repo()
        cfg = Path(t, "cfg.sh")
        cfg.write_text(f'source "{CONFIG}"\nFIGMA_MCP_PREFIX="mcp__figma-test"\n', encoding="utf-8")
        r = _install(t, cfg)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(
            "tools: Read, Grep, Glob, mcp__figma-test__get_design_context, mcp__figma-test__get_screenshot",
            _tools_line(Path(t, AGENT)),
        )
        self.assertIsNone(PLACEHOLDER.search(Path(t, AGENT).read_text(encoding="utf-8")))

    def test_reinstall_treats_the_rendered_agent_as_pristine(self):
        # The pristine check renders through the same function, so an untouched install
        # must never be reported as "edited locally" on the next upgrade.
        t = self.repo()
        self.assertEqual(0, _install(t).returncode)
        r = _install(t)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertNotIn("edited locally", r.stdout)

    def test_consumer_doctor_fails_on_a_leaked_placeholder(self):
        t = self.repo()
        self.assertEqual(0, _install(t).returncode)
        a = Path(t, AGENT)
        a.write_text(
            a.read_text(encoding="utf-8").replace(
                "tools: Read, Grep, Glob", "tools: Read, Grep, Glob, {{FIGMA_MCP_PREFIX}}__get_screenshot"
            ),
            encoding="utf-8",
        )
        r = subprocess.run(
            ["bash", str(Path(t, "agents/neyra-dev-kit/doctor.sh"))], capture_output=True, text=True, cwd=t
        )
        self.assertNotEqual(0, r.returncode, r.stdout)
        self.assertIn("unrendered {{...}} placeholder", r.stdout)
        self.assertIn("solution-designer.md", r.stdout)

    def test_routine_spec_is_verbatim_and_identical_across_installs(self):
        a, b = self.repo(), self.repo()
        for t in (a, b):
            self.assertEqual(0, _install(t).returncode)
        sa = Path(a, ROUTINE).read_text(encoding="utf-8")
        sb = Path(b, ROUTINE).read_text(encoding="utf-8")
        self.assertEqual(sa, sb)
        self.assertEqual(sa, (KIT / "routines" / "doc-freshness.SKILL.md").read_text(encoding="utf-8"))
        self.assertNotIn(a, sa)
        self.assertNotIn("{{REPO_PATH}}", sa)
        self.assertNotIn("cd /", sa)


if __name__ == "__main__":
    unittest.main()
