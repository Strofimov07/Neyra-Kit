#!/usr/bin/env python3
"""Regression tests for portable automated-reviewer instructions."""

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class PortableReviewerTests(unittest.TestCase):
    def test_pr_review_watch_uses_gh_repo_placeholders_and_parses_severity(self):
        for relative in (
            "agents/dev-skills/pr-review-watch/SKILL.md",
            ".claude/agents/pr-review-watch.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
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
