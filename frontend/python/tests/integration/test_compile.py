from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, cast

import pytest
from hypothesis import given
from hypothesis import strategies as st

from units import Unit, UnitsCompileError, compile
from units.quantity import Quantity

type Meter = Annotated[Quantity, Unit("meter")]
type Centimeter = Annotated[Quantity, Unit("centimeter")]
type Second = Annotated[Quantity, Unit("second")]
type MetersPerSecond = Annotated[Quantity, Unit("meter / second")]


@dataclass(frozen=True)
class CompiledCase:
    ref: Callable[..., float]
    native: Callable[..., float]
    inputs: st.SearchStrategy[tuple[float, ...]]


scalar = st.floats(allow_nan=False)


def double(x: Meter) -> Meter:
    return x + x


def copied(x: Meter) -> Meter:
    y = x
    return y


def advance(x: Meter, v: MetersPerSecond, dt: Second) -> Meter:
    dx = v * dt
    pos = x + dx
    return pos


def repeat(x: Meter) -> Meter:
    for _ in range(3):
        x = x + x
    return x


def repeat_with_step(x: Meter) -> Meter:
    for _ in range(1, 5, 2):
        x = x + x
    return x


def repeat_with_target(x: Meter) -> Meter:
    for i in range(3):
        x = x + x
    return x


@pytest.fixture(
    scope="module",  # compile functions once
    params=[
        pytest.param(
            (double, st.tuples(scalar)),
            id=double.__name__,
        ),
        pytest.param(
            (copied, st.tuples(scalar)),
            id="local-alias",
        ),
        pytest.param(
            (
                advance,
                st.tuples(scalar, scalar, scalar),
            ),
            id="multi-argument",
        ),
        pytest.param(
            (repeat, st.tuples(scalar)),
            id="for-range",
        ),
        pytest.param(
            (repeat_with_step, st.tuples(scalar)),
            id="for-range-with-step",
        ),
        pytest.param(
            (repeat_with_target, st.tuples(scalar)),
            id="for-range-with-target",
        ),
    ],
)
def compiled_case(request: pytest.FixtureRequest) -> CompiledCase:
    source, inputs = request.param
    return CompiledCase(
        ref=cast(Callable[..., float], source),
        native=compile(source),
        inputs=inputs,
    )


@given(data=st.data())
def test_compiled_matches_python(
    compiled_case: CompiledCase,
    data: st.DataObject,
) -> None:
    args = data.draw(compiled_case.inputs, label="arguments")
    expected = compiled_case.ref(*args)
    actual = compiled_case.native(*args)
    assert actual == pytest.approx(expected, nan_ok=True)


# TODO(jwh): Conversion has to be tested separately b/c we don't have a Python-side `to` call to compare against.
def test_convert_units():
    @compile
    def meter_to_centimeter(x: Meter) -> Centimeter:
        return x.to("cm")

    assert meter_to_centimeter(1.0) == pytest.approx(100.0)
    assert meter_to_centimeter(1e-2) == pytest.approx(1.0)


def test_compile_invalid():
    def double_invalid(x: Meter) -> Meter:
        return x * x

    with pytest.raises(UnitsCompileError):
        compile(double_invalid)
