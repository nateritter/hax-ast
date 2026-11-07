"""Extract the structure of Python source into a compact tree or JSON."""

from __future__ import annotations

from typing import Final, Union

JsonPrimitive = Union[None, bool, int, float, str]
JsonValue = Union[JsonPrimitive, list["JsonValue"], dict[str, "JsonValue"]]
JsonObject = dict[str, JsonValue]

VERSION: Final = "0.1.0"


class AstError(Exception):
    """Raised when source cannot be parsed or read."""