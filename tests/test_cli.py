from __future__ import annotations

import io
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

from support import ROOT
from hax_ast import VERSION


class CliTests(unittest.TestCase):
    def test_tree_output_lists_nodes_and_line_numbers(self) -> None:
        source = "x = 1\ny = x + 2\n"
        stdout = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(source)):
            with mock.patch("sys.stdout", stdout):
                from hax_ast import cli

                cli.main(["-"])
        self.assertIn("Module", stdout.getvalue())
        self.assertIn("Assign", stdout.getvalue())
        self.assertIn("line 1", stdout.getvalue())
        self.assertIn("line 2", stdout.getvalue())

    def test_json_output_is_full_ast(self) -> None:
        import json

        source = "x = 1\n"
        stdout = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(source)):
            with mock.patch("sys.stdout", stdout):
                from hax_ast import cli

                cli.main(["-", "--json"])
        tree = json.loads(stdout.getvalue())
        self.assertEqual(tree["type"], "Module")
        self.assertEqual(tree["body"][0]["type"], "Assign")

    def test_syntax_error_exits_nonzero(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("def f(:\n")):
            with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
                from hax_ast import cli

                with self.assertRaises(SystemExit) as raised:
                    cli.main(["-"])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("invalid syntax", stderr.getvalue())

    def test_unreadable_file_exits_nonzero(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            from hax_ast import cli

            with self.assertRaises(SystemExit) as raised:
                cli.main(["does-not-exist.py"])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("cannot read", stderr.getvalue())

    def test_launcher_works_through_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            link = pathlib.Path(directory) / "hax-ast"
            link.symlink_to(ROOT / "hax-ast")
            result = subprocess.run(
                [str(link), "--version"],
                check=False,
                text=True,
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"hax-ast {VERSION}")

    def test_launcher_ignores_modules_in_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pathlib.Path(directory, "json.py").write_text("raise SystemExit('shadowed')\n")
            result = subprocess.run(
                [str(ROOT / "hax-ast"), "--version"],
                check=False,
                text=True,
                capture_output=True,
                cwd=directory,
            )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()