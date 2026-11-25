"""Evaluate postfix operations on a typed stack without Python eval."""

import math
import operator

from errors import LanguageError

OPERATIONS = {
    "+": (2, operator.add),
    "sqrt": (1, math.sqrt),
    "pow": (2, math.pow),
}
SINGLE_RESULT = 1


def apply_operation(stack, token):
    """Pop operands in source order and push one finite numeric result."""
    operation = str(token).removesuffix("()")
    arity, function = OPERATIONS[operation]
    if len(stack) < arity:
        raise LanguageError(f"{operation}: not enough operands")
    operands = stack[-arity:]
    if any(not isinstance(value, (int, float)) for value in operands):
        raise LanguageError(f"{operation}: numeric operands required")
    try:
        result = function(*operands)
    except (ValueError, OverflowError) as error:
        raise LanguageError(f"{operation}: {error}") from error
    if not math.isfinite(result):
        raise LanguageError(f"{operation}: non-finite result")
    del stack[-arity:]
    stack.append(result)


def finish_expression(stack):
    """Require exactly one value after all postfix items are consumed."""
    if len(stack) != SINGLE_RESULT:
        raise LanguageError("expression must produce exactly one value")
    return stack[0]
