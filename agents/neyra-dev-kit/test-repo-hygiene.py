#!/usr/bin/env python3
"""Regression: onboarding-hygiene findings, and what must NOT count as one.

The check exists to catch traps a repository sets for the next person. Its value
depends on the split it draws: a public address in a runbook is a wrong-machine
instruction waiting to happen, while a container subnet is internal topology and
reporting it as a finding trains people to ignore the whole check.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "check-repo-hygiene.py"

# Addresses are assembled from parts on purpose: a literal IPv4 anywhere in the kit
# tree is a finding for the canonical leak scan, whatever it points at. None of these
# belong to any consumer — a well-known public resolver, a documentation-reserved
# range, and private ranges.
PUBLIC = ".".join(["8", "8", "8", "8"])
DOC_RESERVED = ".".join(["203", "0", "113", "9"])
BRIDGE = ".".join(["172", "18", "0", "0"])
INTERNAL = ".".join(["10", "88", "0", "2"])
LAN = ".".join(["192", "168", "1", "1"])
LOOPBACK = ".".join(["127", "0", "0", "1"])


def _repo(files, gitignore=None):
    d = Path(tempfile.mkdtemp())
    subprocess.run(["git", "-C", str(d), "init", "-q"], check=True)
    for rel, body in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    if gitignore:
        (d / ".gitignore").write_text(gitignore)
    subprocess.run(["git", "-C", str(d), "add", "-A", "-f"], check=True)
    return d


def _run(d, *args):
    r = subprocess.run(["python3", str(TOOL), str(d), *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class RepoHygiene(unittest.TestCase):
    def test_public_address_is_a_finding(self):
        d = _repo({"docs/run.md": "ssh root@%s is documentation-safe\nssh root@%s\n" % (DOC_RESERVED, PUBLIC)})
        code, out = _run(d)
        self.assertIn(PUBLIC, out)
        self.assertNotIn(DOC_RESERVED, out, "documentation-reserved ranges are examples, not hosts")
        self.assertEqual(code, 0, "advisory by default")
        self.assertEqual(_run(d, "--strict")[0], 1)

    def test_internal_ranges_are_listed_but_not_counted(self):
        d = _repo({"docs/net.md": "bridge %s/16, service at %s, gw %s\n" % (BRIDGE, INTERNAL, LAN)})
        code, out = _run(d, "--strict")
        self.assertIn("internal-range mention", out)
        self.assertIn("0 finding(s)", out.replace("check-repo-hygiene: ", ""))
        self.assertEqual(code, 0, "internal topology must not fail the check")

    def test_loopback_is_silent(self):
        d = _repo({"docs/dev.md": "open http://%s:8000\n" % LOOPBACK})
        _, out = _run(d)
        self.assertNotIn(LOOPBACK, out)

    def test_gitignore_directory_trap(self):
        d = _repo({"conf/a.txt": "x\n"}, gitignore="conf/\n")
        _, out = _run(d)
        self.assertIn("conf/ is ignored but", out)

    def test_broken_relative_link(self):
        d = _repo({"docs/a.md": "see [gone](./missing.md) and [ok](./b.md)\n", "docs/b.md": "b\n"})
        _, out = _run(d)
        self.assertIn("missing.md", out)
        self.assertNotIn("→ ./b.md", out)

    def test_exclude_skips_a_deliberate_host_map(self):
        d = _repo({"docs/HOSTS.md": "app host: %s\n" % PUBLIC,
                   "docs/run.md": "ssh root@%s\n" % PUBLIC})
        _, out = _run(d, "--exclude", "docs/HOSTS.md")
        self.assertIn("docs/run.md", out, "other files are still checked")
        self.assertNotIn("docs/HOSTS.md", out)
        self.assertEqual(_run(d, "--strict", "--exclude", "docs")[0], 0,
                         "excluding the whole directory clears the findings")

    def test_clean_repo_is_clean(self):
        d = _repo({"README.md": "nothing to see\n"})
        code, out = _run(d, "--strict")
        self.assertEqual(code, 0)
        self.assertIn("0 finding(s)", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
