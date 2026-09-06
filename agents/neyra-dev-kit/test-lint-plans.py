#!/usr/bin/env python3
"""Regression: lint-plans tells a placeholder from the Linear status word (NEB-1800).

`Todo` in task-anchor prose ("NEB-476 remains `Todo`") is a status, not a placeholder;
`TODO` is. Matching the bare token case-insensitively kept a consumer's doctor red on
26 plan docs, which trains everyone to skim past the failures.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent
LINT = KIT / "lint-plans.py"


def lint(text):
    with tempfile.TemporaryDirectory() as tmp:
        plan = Path(tmp, "plan.md")
        plan.write_text(text, encoding="utf-8")
        r = subprocess.run([sys.executable, str(LINT), str(plan)], capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr


class LintPlansTests(unittest.TestCase):
    def test_linear_status_word_passes(self):
        rc, out = lint(
            "NEB-476 remains urgent/P0 `Todo`; its calculation and legal gates are unchanged.\n"
            "- Read-only urgent Todo refresh: NEB-484 remains the nearest urgent item.\n"
        )
        self.assertEqual(rc, 0, out)

    def test_uppercase_placeholder_tokens_fail(self):
        for text in ("- TODO: wire the endpoint\n", "// TODO later\n", "value: TBD\n", "FIXME before merge\n"):
            rc, out = lint(text)
            self.assertEqual(rc, 1, text + out)

    def test_phrase_placeholders_stay_case_insensitive(self):
        for text in ("Step 3: Implement Later.\n", "Step 4: Similar To The Above.\n", "then Add Validation\n"):
            rc, out = lint(text)
            self.assertEqual(rc, 1, text + out)

    def test_lowercase_prose_word_is_not_a_placeholder(self):
        rc, out = lint("The todo list in the app shows three items; nothing is tbd here.\n")
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
