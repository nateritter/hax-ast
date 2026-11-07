# hax-ast

A zero-dependency CLI for extracting the structure of Python source files as a compact tree or
JSON, for [hax](https://github.com/OleksandrChekhovskyi/hax).

`hax-ast` parses a file with Python's built-in `ast` module and prints its syntax tree: node
types, key fields, and the source line each node starts on. Giving hax the structure before a
code edit helps it reason about scope and nesting instead of guessing from indentation alone,
which is especially useful for lightweight or local models.

## Requirements

- Python 3.9 or newer
- No pip dependencies; standard library only

## Usage

```sh
./hax-ast src/module.py
./hax-ast src/module.py --json
cat src/module.py | ./hax-ast -
```

The default output is a compact indented tree; `--json` writes the full AST. Errors go to stderr
with exit status 1.

## Installation

Clone the repository somewhere it will not be moved, then run:

```sh
./install.sh
```

The installer links `hax-ast` into `~/.local/bin` and the skill into hax's skills directory. It
is safe to rerun and refuses to replace existing paths. Restart hax after installing the skill.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)