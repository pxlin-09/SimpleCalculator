"""Evaluate arithmetic equations using the calculator operations.

The evaluator intentionally does not use Python's ``eval``.  It parses the
small expression language supported by this project, so arbitrary input cannot
execute code.
"""

import re

from add import add
from div import div
from mut import mut
from power import power
from sub import sub


_NUMBER = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)")
_OPERATORS = set("+-*/^()[]{}")


class _Parser:
    def __init__(self, expression):
        self.tokens = self._tokenize(expression)
        self.position = 0

    @staticmethod
    def _tokenize(expression):
        tokens = []
        position = 0
        while position < len(expression):
            if expression[position].isspace():
                position += 1
                continue

            number = _NUMBER.match(expression, position)
            if number:
                tokens.append(("number", number.group()))
                position = number.end()
                continue

            if expression.startswith("**", position):
                tokens.append(("operator", "^"))
                position += 2
                continue

            character = expression[position]
            if character in _OPERATORS:
                tokens.append(("operator", character))
                position += 1
                continue

            raise ValueError("invalid character")

        return tokens

    def _current(self):
        if self.position == len(self.tokens):
            return None
        return self.tokens[self.position][1]

    def _accept(self, token):
        if self._current() == token:
            self.position += 1
            return True
        return False

    def parse(self):
        if not self.tokens:
            raise ValueError("empty expression")
        result = self._additive()
        if self._current() is not None:
            raise ValueError("unexpected token")
        return result

    def _additive(self):
        result = self._multiplicative()
        while True:
            if self._accept("+"):
                result = add(result, self._multiplicative())
            elif self._accept("-"):
                result = sub(result, self._multiplicative())
            else:
                return result

    def _multiplicative(self):
        result = self._unary()
        while True:
            if self._accept("*"):
                result = mut(result, self._unary())
            elif self._accept("/"):
                result = div(result, self._unary())
                if result is None:
                    raise ValueError("division by zero")
            else:
                return result

    def _unary(self):
        if self._accept("+"):
            return self._unary()
        if self._accept("-"):
            return sub(0, self._unary())
        return self._power()

    def _power(self):
        result = self._primary()
        if self._accept("^"):
            # Recursing through unary makes exponentiation right associative
            # and permits expressions such as 2^-3.
            result = power(result, self._unary())
        return result

    def _primary(self):
        current = self._current()
        if current is None:
            raise ValueError("missing operand")

        if self.tokens[self.position][0] == "number":
            self.position += 1
            return float(current) if "." in current else int(current)

        opening = current
        closing = {"(": ")", "[": "]", "{": "}"}.get(opening)
        if closing is None:
            raise ValueError("missing operand")
        self.position += 1
        result = self._additive()
        if not self._accept(closing):
            raise ValueError("unclosed bracket")
        return result


def eval(equation):
    """Return the result of *equation*, or ``None`` when it is invalid."""
    if not isinstance(equation, str):
        return None
    try:
        result = _Parser(equation).parse()
        # The calculator handles real numbers; a fractional power of a
        # negative number should therefore be treated as invalid input rather
        # than leaking a complex result to callers.
        return None if isinstance(result, complex) else result
    except (ArithmeticError, TypeError, ValueError, OverflowError):
        return None


# Descriptive aliases make the function convenient to use without changing
# the public ``eval`` name used by the issue examples.
evaluate = eval
solve = eval
