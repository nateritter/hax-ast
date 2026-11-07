from __future__ import annotations

import argparse
import pathlib
import sys
from collections.abc import Sequence
from typing import Optional

from . import VERSION, AstError
from .ast_extract import extract, extract_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hax-ast",
        description="Extract the structure of Python source into a compact tree or JSON.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "file", help="Python source file to parse, or - to read standard input"
    )
    parser.add_argument("--json", action="store_true", help="write the AST as JSON")
    return parser


def read_source(arg: str) -> tuple[str, str]:
    """Return (source, filename) for a file argument or stdin when arg is '-'."""
    if arg == "-":
        return sys.stdin.read(), "<stdin>"
    path = pathlib.Path(arg)
    try:
        return path.read_text(encoding="utf-8"), str(path)
    except OSError as error:
        raise AstError(f"cannot read {arg}: {error}") from error


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        source, filename = read_source(args.file)
        output = extract_json(source, filename) if args.json else extract(source, filename)
    except AstError as error:
        print(f"hax-ast: {error}", file=sys.stderr)
        raise SystemExit(1)
    sys.stdout.write(output if output.endswith("\n") else output + "\n")


def run() -> None:
    try:
        main()
    except BrokenPipeError:
        raise SystemExit(0)