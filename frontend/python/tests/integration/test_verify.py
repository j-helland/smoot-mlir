from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, cast

import pytest
from hypothesis import given
from hypothesis import strategies as st

from units import Quantity, Unit, UnitsCompileError, verify

type Meter = Annotated[Quantity, Unit("meter")]
type Second = Annotated[Quantity, Unit("second")]
type MetersPerSecond = Annotated[Quantity, Unit("meter / second")]


@dataclass(frozen=True)
class VerifiedCase:
    ref: Callable[..., float]
    verified: Callable[..., float]
    inputs: st.SearchStrategy[tuple[float, ...]]


scalar = st.floats(allow_nan=False)


def distance(velocity: MetersPerSecond, dt: Second) -> Meter:
    return velocity * dt


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
        j = i + 1  # noqa: F841
        x = x + x
    return x


@pytest.fixture(
    scope="module",  # compile functions once
    params=[
        pytest.param(
            (distance, st.tuples(scalar, scalar)),
            id=distance.__name__,
        ),
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
def verified_case(request: pytest.FixtureRequest) -> VerifiedCase:
    source, inputs = request.param
    return VerifiedCase(
        ref=cast(Callable[..., float], source),
        verified=verify(source),
        inputs=inputs,
    )


@given(data=st.data())
def test_verified_matches_python(
    verified_case: VerifiedCase,
    data: st.DataObject,
) -> None:
    args = data.draw(verified_case.inputs, label="arguments")
    expected = verified_case.ref(*args)
    actual = verified_case.verified(*args)
    assert actual == pytest.approx(expected, nan_ok=True)


def test_verify_invalid():
    """Verify that the compiler backend fails on an invalid computation."""

    def distance_invalid(velocity: MetersPerSecond, dt: Second) -> Meter:
        return velocity + dt

    with pytest.raises(UnitsCompileError):
        verify(distance_invalid)
