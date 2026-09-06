#!/usr/bin/env python3
"""Regression: post-tool-use-format.sh formats Python with the formatter the repo DECLARED (NEB-1901).

Any pyproject.toml used to count as a ruff opt-in. A consumer declaring [tool.black] and
[tool.ruff] (ruff as linter) with CI gating on black got its untouched hunks rewritten in
black>=24 style by `ruff format`, and CI lint went red. The hook now follows the declaration:
black beats ruff, and a bare pyproject.toml formats nothing.
"""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

KIT = pathlib.Path(__file__).resolve().parent
HOOK = KIT / "hooks" / "post-tool-use-format.sh"


class FormatHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.target = self.root / "mod.py"
        self.target.write_text("x=1\n", encoding="utf-8")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "fmt.log"
        # Fake formatters: each appends "<name> <args>" to the shared log instead of formatting.
        for name in ("black", "ruff"):
            fake = self.bin / name
            fake.write_text(
                "#!/usr/bin/env bash\nprintf '%s %s\\n' " + name + " \"$*\" >> \"$NEYRA_FMT_LOG\"\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self):
        payload = {"tool_input": {"file_path": str(self.target)}}
        r = subprocess.run(
            [str(HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
            cwd=self.root,
            env={
                **os.environ,
                "NEYRA_FMT_LOG": str(self.log),
                "CLAUDE_PROJECT_DIR": str(self.root),
                "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}",
            },
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []

    def test_black_wins_when_both_are_declared(self):
        (self.root / "pyproject.toml").write_text(
            "[tool.black]\nline-length = 100\n\n[tool.ruff]\nline-length = 100\n", encoding="utf-8"
        )
        self.assertEqual(self.run_hook(), [f"black -q {self.target}"])

    def test_ruff_when_only_ruff_is_declared(self):
        (self.root / "pyproject.toml").write_text("[tool.ruff.lint]\nselect = ['E']\n", encoding="utf-8")
        self.assertEqual(self.run_hook(), [f"ruff format {self.target}"])

    def test_ruff_toml_declares_ruff(self):
        (self.root / "ruff.toml").write_text("", encoding="utf-8")
        self.assertEqual(self.run_hook(), [f"ruff format {self.target}"])

    def test_pre_commit_black_pin_selects_black_over_ruff_config(self):
        (self.root / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: https://github.com/psf/black\n    rev: 23.12.1\n    hooks:\n      - id: black\n",
            encoding="utf-8",
        )
        (self.root / "pyproject.toml").write_text("[tool.ruff]\nline-length = 100\n", encoding="utf-8")
        self.assertEqual(self.run_hook(), [f"black -q {self.target}"])

    def test_pre_commit_hook_id_with_trailing_comment_still_counts(self):
        (self.root / ".pre-commit-config.yaml").write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: black   # pinned in requirements.txt\n"
            "      - id: blacken-docs\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_hook(), [f"black -q {self.target}"])

    def test_bare_pyproject_formats_nothing(self):
        (self.root / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
        self.assertEqual(self.run_hook(), [])

    def test_no_config_formats_nothing(self):
        self.assertEqual(self.run_hook(), [])


if __name__ == "__main__":
    unittest.main()
