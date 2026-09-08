from add import add
from div import div
from mut import mut
from power import power
from sub import sub


def test_add():
    assert add(2, 3) == 5


def test_sub():
    assert sub(5, 3) == 2


def test_mut():
    assert mut(4, 3) == 12


def test_div():
    assert div(10, 2) == 5


def test_div_by_zero_returns_none():
    assert div(10, 0) is None


def test_power():
    assert power(2, 3) == 8


def test_power_zero_exponent():
    assert power(7, 0) == 1


def test_power_negative_exponent():
    assert power(2, -2) == 0.25
