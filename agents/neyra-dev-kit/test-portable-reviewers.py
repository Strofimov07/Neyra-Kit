#!/usr/bin/env python3
"""Regression tests for portable automated-reviewer instructions.

A consumer may legitimately not have a given wrapper installed: since v0.41.0 the
product profile selects the agent set, and v0.43.0 extended that to pr-review-watch.
An absent wrapper is then a correct install, not a regression — but only when the
profile actually deselected it. Anything else absent is still a failure.
"""

import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = pathlib.Path(__file__).resolve().parent


def deselected(agent):
    """True when settings/product.yml declares this agent out of scope for the repo."""
    tool = KIT / "product-profile.py"
    if not tool.is_file():
        return False
    try:
        out = subprocess.run([sys.executable, str(tool), str(ROOT), "--skip-agents"],
                             capture_output=True, text=True).stdout
    except OSError:
        return False
    return agent in out.split()


class PortableReviewerTests(unittest.TestCase):
    def test_pr_review_watch_uses_gh_repo_placeholders_and_parses_severity(self):
        for relative in (
            "agents/dev-skills/pr-review-watch/SKILL.md",
            ".claude/agents/pr-review-watch.md",
        ):
            path = ROOT / relative
            if not path.is_file() and relative.startswith(".claude/") and deselected("pr-review-watch"):
                self.skipTest("pr-review-watch is out of scope for this repo per settings/product.yml")
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("repos/:owner/:repo", text, relative)
            self.assertIn("repos/{owner}/{repo}", text, relative)
            self.assertIn('.body | scan("High Severity|Medium Severity|Low Severity")', text, relative)

    def test_security_reviewer_has_no_product_specific_default_scope(self):
        skill = (ROOT / "agents/dev-skills/security-review/SKILL.md").read_text(
            encoding="utf-8"
        )
        wrapper = (ROOT / ".claude/agents/security-reviewer.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("Neyra stack", skill)
        self.assertNotIn("Neyra monorepo", wrapper)


if __name__ == "__main__":
    unittest.main()
