"""Parse Python source and render its syntax tree."""

from __future__ import annotations

import ast
import json
from typing import Any

from . import AstError


def parse(source: str, filename: str) -> ast.AST:
    try:
        return ast.parse(source, filename=filename)
    except SyntaxError as error:
        raise AstError(f"{filename}: {error}") from error


def node_label(node: ast.AST) -> str:
    """A short, human-readable label for a node: its type plus identifying fields."""
    type_name = type(node).__name__
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return f"{type_name}: {node.name}"
    if isinstance(node, ast.Name):
        return f"{type_name}: {node.id}"
    if isinstance(node, ast.arg):
        return f"{type_name}: {node.arg}"
    if isinstance(node, ast.Attribute):
        return f"{type_name}: {node.attr}"
    if isinstance(node, ast.alias):
        return f"{type_name}: {node.name}" + (f" as {node.asname}" if node.asname else "")
    if isinstance(node, ast.BinOp):
        return f"{type_name}: {type(node.op).__name__}"
    if isinstance(node, ast.UnaryOp):
        return f"{type_name}: {type(node.op).__name__}"
    if isinstance(node, ast.Compare):
        return f"{type_name}: {' '.join(type(op).__name__ for op in node.ops)}"
    if isinstance(node, ast.Constant):
        text = repr(node.value)
        return f"{type_name}: {text}" if len(text) <= 40 else f"{type_name}: {type(node.value).__name__}"
    return type_name


def dump(node: ast.AST, depth: int = 0) -> list[str]:
    """Render a tree as indented lines, one node per line, with source locations."""
    indent = "  " * depth
    line_no = getattr(node, "lineno", None)
    location = f" (line {line_no})" if line_no is not None else ""
    lines = [f"{indent}{node_label(node)}{location}"]
    for child in ast.iter_child_nodes(node):
        lines.extend(dump(child, depth + 1))
    return lines


def extract(source: str, filename: str) -> str:
    """Return the compact indented tree for `source`."""
    return "\n".join(dump(parse(source, filename)))


def extract_json(source: str, filename: str) -> str:
    """Return the full AST as JSON, with source locations preserved."""
    tree = parse(source, filename)

    def serialize(node: Any) -> Any:
        if isinstance(node, ast.AST):
            fields = {
                key: serialize(value)
                for key, value in ast.iter_fields(node)
                if key not in ("type_ignores",)
            }
            return {"type": type(node).__name__, **fields}
        if isinstance(node, list):
            return [serialize(item) for item in node]
        return node

    return json.dumps(serialize(tree), indent=2, ensure_ascii=False)