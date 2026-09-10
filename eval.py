"""Evaluate arithmetic equations using the calculator operations."""

import re

from add import add
from div import div
from mut import mut
from power import power
from sub import sub


_NUMBER = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)")
_OPENING_BRACKETS = {"(": ")", "[": "]", "{": "}"}


class _Parser:
    """Small recursive-descent parser for the calculator grammar."""

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
                text = number.group(0)
                tokens.append(float(text) if "." in text else int(text))
                position = number.end()
                continue

            character = equation[position]
            if character in "+-*/^()[]{}":
                tokens.append(character)
                position += 1
                continue

            raise ValueError("invalid character in equation")
        return tokens

    def _current(self):
        if self.position == len(self.tokens):
            return None
        return self.tokens[self.position]

    def _take(self, token):
        if self._current() != token:
            raise ValueError("unexpected token")
        self.position += 1

    def parse(self):
        if not self.tokens:
            raise ValueError("empty equation")
        result = self._additive()
        if self._current() is not None:
            raise ValueError("trailing token")
        return result

    def _additive(self):
        result = self._multiplicative()
        while self._current() in ("+", "-"):
            operator = self._current()
            self.position += 1
            right = self._multiplicative()
            result = add(result, right) if operator == "+" else sub(result, right)
        return result

    def _multiplicative(self):
        result = self._unary()
        while self._current() in ("*", "/"):
            operator = self._current()
            self.position += 1
            right = self._unary()
            result = mut(result, right) if operator == "*" else div(result, right)
            if result is None:
                raise ValueError("division by zero")
        return result

    def _unary(self):
        # Keeping unary operators outside _power gives -2^2 == -(2^2).
        if self._current() in ("+", "-"):
            operator = self._current()
            self.position += 1
            value = self._unary()
            return value if operator == "+" else sub(0, value)
        return self._power()

    def _power(self):
        result = self._primary()
        if self._current() == "^":
            self.position += 1
            result = power(result, self._unary())
        return result

    def _primary(self):
        current = self._current()
        if isinstance(current, (int, float)):
            self.position += 1
            return current
        if current in _OPENING_BRACKETS:
            self.position += 1
            result = self._additive()
            self._take(_OPENING_BRACKETS[current])
            return result
        raise ValueError("expected number or opening bracket")


def eval(equation):
    """Return the result of an arithmetic equation, or ``None`` if invalid.

    The supported operators are ``+``, ``-``, ``*``, ``/``, and ``^``.
    Parentheses, brackets, whitespace, signed values, and decimal values are
    accepted.
    """
    if not isinstance(equation, str):
        return None
    try:
        return _Parser(equation).parse()
    except (ArithmeticError, TypeError, ValueError, OverflowError):
        return None
