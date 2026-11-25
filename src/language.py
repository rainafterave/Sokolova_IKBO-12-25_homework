"""Parse variant 23 configurations using a Lark grammar."""

import json
import math
from pathlib import Path

from lark import Lark
from lark.exceptions import UnexpectedInput

from errors import LanguageError
from expressions import apply_operation, finish_expression

GRAMMAR = Path(__file__).with_name("grammar.lark")


def read_number(token):
    """Convert a decimal token and reject non-finite JSON values."""
    value = float(token)
    if not math.isfinite(value):
        raise LanguageError("number is outside the supported finite range")
    return value


def evaluate_dictionary(node, constants):
    """Evaluate ordered fields using dictionary-local constant declarations."""
    result = {}
    local = constants.copy()
    for child in node.children:
        if child.data == "declaration":
            declare(child, local)
        else:
            name, value = child.children
            if name in result:
                raise LanguageError(f"duplicate dictionary key: {name}")
            result[str(name)] = evaluate(value, local)
    return result


def declare(node, constants):
    """Bind a previously unused name after evaluating its value."""
    name, value = node.children
    if name in constants:
        raise LanguageError(f"constant already declared: {name}")
    constants[str(name)] = evaluate(value, constants)


def evaluate_expression(node, constants):
    """Evaluate values, references and operators in postfix source order."""
    stack = []
    for child in node.children:
        if child.data == "operation":
            apply_operation(stack, child.children[0])
        else:
            stack.append(evaluate(child, constants))
    return finish_expression(stack)


def evaluate(node, constants):
    """Evaluate a parsed value, resolving only already declared constants."""
    if node.data == "number":
        return read_number(node.children[0])
    if node.data == "string":
        return json.loads(node.children[0])
    if node.data == "dictionary":
        return evaluate_dictionary(node, constants)
    if node.data == "expression":
        return evaluate_expression(node, constants)
    name = str(node.children[0])
    if name not in constants:
        raise LanguageError(f"undefined constant: {name}")
    return constants[name]


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
    constants = {}
    *declarations, value = tree.children
    for declaration in declarations:
        declare(declaration, constants)
    return evaluate(value, constants)
