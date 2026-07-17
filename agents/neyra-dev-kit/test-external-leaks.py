#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check-external-leaks.py")
SPEC = importlib.util.spec_from_file_location("check_external_leaks", MODULE_PATH)
check_external_leaks = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check_external_leaks)


class ExternalLeakTests(unittest.TestCase):
    def scan_text(self, content: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "artifact.txt").write_text(content, encoding="utf-8")
            return check_external_leaks.scan(Path(tmp))

    def test_allows_loopback(self):
        self.assertEqual([], self.scan_text("Preview: http://127.0.0.1:3000"))

    def test_rejects_non_loopback_ip(self):
        address = ".".join(["10", "12", "13", "14"])
        self.assertTrue(self.scan_text(f"Server: {address}"))

    def test_rejects_other_internal_references(self):
        self.assertTrue(self.scan_text("Read docs/memory-bank before release"))


if __name__ == "__main__":
    unittest.main()
