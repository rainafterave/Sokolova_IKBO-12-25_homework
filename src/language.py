"""Parse variant 23 configurations using a Lark grammar."""

import json
import math
from pathlib import Path

from lark import Lark
from lark.exceptions import UnexpectedInput

GRAMMAR = Path(__file__).with_name("grammar.lark")


class LanguageError(ValueError):
    """Report a syntax or evaluation error in a configuration."""


def read_number(token):
    """Convert a decimal token and reject non-finite JSON values."""
    value = float(token)
    if not math.isfinite(value):
        raise LanguageError("number is outside the supported finite range")
    return value


def evaluate(node):
    """Convert a parsed literal tree into a JSON-compatible value."""
    if node.data == "number":
        return read_number(node.children[0])
    if node.data == "string":
        return json.loads(node.children[0])
    result = {}
    for pair in node.children:
        name, value = pair.children
        if name in result:
            raise LanguageError(f"duplicate dictionary key: {name}")
        result[str(name)] = evaluate(value)
    return result


def parse(source):
    """Parse one root value and raise readable syntax errors."""
    parser = Lark.open(str(GRAMMAR), parser="lalr")
    try:
        tree = parser.parse(source)
    except UnexpectedInput as error:
        message = (
            f"syntax error at line {error.line}, column {error.column}\n"
            f"{error.get_context(source)}"
        )
        raise LanguageError(message) from error
    return evaluate(tree.children[0])
