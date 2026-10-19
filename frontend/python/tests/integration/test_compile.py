from typing import Annotated, TypeAlias

import pytest
from units import Quantity, Unit, UnitsCompileError, compile

Meter: TypeAlias = Annotated[Quantity, Unit("meter")]


def test_compile_happy_path():
    @compile
    def double(x: Meter) -> Meter:
        return x + x


def test_compile_invalid():
    def double_invalid(x: Meter) -> Meter:
        return x * x

    with pytest.raises(UnitsCompileError):
        compile(double_invalid)
