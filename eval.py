"""Evaluate arithmetic equations using the calculator's operations.

The public :func:`eval` function deliberately does not use Python's built-in
``eval``. Equations are tokenised and parsed here so that arbitrary Python
code can never be executed.
"""

import math
import re

from add import add
from div import div
from mut import mut
from power import power
from sub import sub


_NUMBER = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
_OPERATORS = ("**", "+", "-", "*", "/", "^", "(", ")")


class _Parser:
    def __init__(self, equation):
        self.tokens = self._tokenize(equation)
        self.position = 0

    @staticmethod
    def _tokenize(equation):
        tokens = []
        position = 0
        while position < len(equation):
            if equation[position].isspace():
                position += 1
                continue

            number = _NUMBER.match(equation, position)
            if number:
                tokens.append(("number", float(number.group())))
                position = number.end()
                continue

            operator = next(
                (operator for operator in _OPERATORS if equation.startswith(operator, position)),
                None,
            )
            if operator is None:
                raise ValueError("invalid character")
            tokens.append(("operator", operator))
            position += len(operator)

        if not tokens:
            raise ValueError("empty equation")
        return tokens

    def _current(self):
        if self.position == len(self.tokens):
            return None
        return self.tokens[self.position]

    def _take(self, operator):
        if self._current() == ("operator", operator):
            self.position += 1
            return True
        return False

    def parse(self):
        result = self._expression()
        if self._current() is not None:
            raise ValueError("unexpected token")
        return result

    def _expression(self):
        result = self._term()
        while True:
            if self._take("+"):
                result = add(result, self._term())
            elif self._take("-"):
                result = sub(result, self._term())
            else:
                return result

    def _term(self):
        result = self._unary()
        while True:
            if self._take("*"):
                result = mut(result, self._unary())
            elif self._take("/"):
                result = div(result, self._unary())
                if result is None:
                    raise ZeroDivisionError
            else:
                return result

    def _unary(self):
        if self._take("+"):
            return self._unary()
        if self._take("-"):
            return sub(0, self._unary())
        return self._power()

    def _power(self):
        result = self._primary()
        if self._take("^") or self._take("**"):
            result = power(result, self._unary())
        return result

    def _primary(self):
        token = self._current()
        if token is None:
            raise ValueError("missing operand")
        if token[0] == "number":
            self.position += 1
            return token[1]
        if self._take("("):
            result = self._expression()
            if not self._take(")"):
                raise ValueError("missing closing bracket")
            return result
        raise ValueError("missing operand")


def eval(equation):
    """Return the result of an arithmetic *equation*, or ``None`` if invalid.

    Supported operators are ``+``, ``-``, ``*``, ``/`` and power (``^`` or
    ``**``). Parentheses, whitespace, signed values, and decimal values are
    supported. Division by zero and non-real/non-finite results are invalid.
    """
    if not isinstance(equation, str):
        return None
    try:
        result = _Parser(equation).parse()
        if isinstance(result, complex) or not math.isfinite(result):
            return None
        return result
    except (ArithmeticError, TypeError, ValueError):
        return None


# A descriptive spelling is useful to callers that do not want to shadow the
# built-in name, while ``eval`` remains the requested public API.
evaluate = eval
