#!/usr/bin/env python3
"""Regression: the skill → subagent map reaches the agent before the first dispatch (NEB-2279 §1).

A consumer agent diffed agents/dev-skills/ against .claude/agents/, counted nine skills
"without a subagent" and dispatched `contract-safety` — which failed, because that skill's
subagent is called contract-checker, four others fire under a different name and five are
manual. `check-skill-mapping.py --agents-status` derives exactly those rows from the mapping
table, and the SessionStart hook injects them. Canonical-only; needs git + the source kit.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
SCRIPT = KIT / "check-skill-mapping.py"
SPEC = importlib.util.spec_from_file_location("check_skill_mapping", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

TABLE = """# Repo

| dev-skill | subagent | fires on |
|---|---|---|
| implementation-loop | implementation-loop | default |
| simplify-diff | code-reviewer | post-implementation |
| goal-mode | (manual — opt-in) | explicit |
| contract-safety | contract-checker | endpoints |
| regression-scout | regression-scout | shared UI |
"""


class AgentsStatusUnitTests(unittest.TestCase):
    def test_only_rows_that_differ_or_are_absent_are_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(TABLE, encoding="utf-8")
            agents = root / ".claude" / "agents"
            agents.mkdir(parents=True)
            for a in ("implementation-loop", "code-reviewer"):
                (agents / f"{a}.md").write_text("x", encoding="utf-8")
            lines = MODULE.agents_status(str(root))
        joined = "\n".join(lines)
        self.assertNotIn("implementation-loop", joined)  # same name, installed → silent
        self.assertIn("- `simplify-diff` → subagent `code-reviewer`", joined)
        self.assertIn("- `goal-mode` — manual, no subagent", joined)
        self.assertIn("`contract-safety` → `contract-checker` not installed: not rendered at install", joined)
        self.assertIn("`regression-scout` → `regression-scout` not installed: MISSING — drift", joined)

    def test_no_table_yields_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual([], MODULE.agents_status(tmp))


class SessionStartInjectionTests(unittest.TestCase):
    def test_dev_consumer_bootstrap_carries_the_map(self):
        tmp = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "init", "-q"], cwd=tmp, check=True, capture_output=True)
            r = subprocess.run(
                ["bash", str(KIT / "install.sh"), "dev", tmp, str(KIT / "configs" / "_product.example.sh")],
                capture_output=True, text=True,
            )
            self.assertEqual(0, r.returncode, r.stderr)
            hook = Path(tmp, "agents/neyra-dev-kit/hooks/session-start.sh")
            out = subprocess.run(
                [str(hook)], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                env={**os.environ, "NEYRA_HOOK_HOST": "codex", "CLAUDE_PROJECT_DIR": tmp},
            )
            self.assertEqual(0, out.returncode, out.stderr)
            ctx = json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("## Skill → subagent map for this repo", ctx)
            self.assertIn("`simplify-diff` → subagent `code-reviewer`", ctx)
            self.assertIn("`goal-mode` — manual, no subagent", ctx)
            self.assertIn("the degraded gate", ctx)
            self.assertNotIn("MISSING — drift", ctx)  # a fresh install has no drift
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
