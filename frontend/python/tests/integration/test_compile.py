from typing import Annotated

import pytest

from units import Quantity, Unit, UnitsCompileError, compile

type Meter = Annotated[Quantity, Unit("meter")]
type Second = Annotated[Quantity, Unit("second")]
type MetersPerSecond = Annotated[Quantity, Unit("meter / second")]


def test_compile_happy_path():
    @compile
    def double(x: Meter) -> Meter:
        return x + x

    assert double(1.0) == pytest.approx(2.0)
    assert double(5.5) == pytest.approx(11.0)


def test_compile_local_alias():
    @compile
    def copied(x: Meter) -> Meter:
        y = x
        return y

    assert copied(1.0) == pytest.approx(1.0)
    assert copied(2.0) == pytest.approx(2.0)


def test_compile_multi_argument():
    @compile
    def advance(x: Meter, v: MetersPerSecond, dt: Second) -> Meter:
        dx = v * dt
        pos = x + dx
        return pos

    assert advance(1.0, 2.0, 3.0) == pytest.approx(7.0)
    assert advance(10.0, 4.0, 0.5) == pytest.approx(12.0)


def test_compile_invalid():
    def double_invalid(x: Meter) -> Meter:
        return x * x

    with pytest.raises(UnitsCompileError):
        compile(double_invalid)
