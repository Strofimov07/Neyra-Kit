#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("lint-scope.py")
SPEC = importlib.util.spec_from_file_location("lint_scope", MODULE_PATH)
lint_scope = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(lint_scope)


class LintScopeIPTests(unittest.TestCase):
    def lint_markdown(self, content: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "SKILL.md").write_text(content, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                return lint_scope.lint([tmp])

    def test_allows_ipv4_loopback(self):
        self.assertEqual(0, self.lint_markdown("Local preview: http://127.0.0.1:3000"))

    def test_rejects_non_loopback_ipv4(self):
        address = ".".join(["10", "12", "13", "14"])
        self.assertEqual(1, self.lint_markdown(f"Server: {address}"))


if __name__ == "__main__":
    unittest.main()
