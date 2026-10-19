from typing import Annotated

import pytest
from units import Quantity, Unit, UnitsCompileError, verify


def test_verify_happy_path():
    @verify
    def distance(
        velocity: Annotated[Quantity, Unit("meter / second")],
        dt: Annotated[Quantity, Unit("second")],
    ) -> Annotated[Quantity, Unit("meter")]:
        return velocity * dt


def test_verify_invalid():
    """Verify that the compiler backend fails on an invalid computation."""

    def distance_invalid(
        velocity: Annotated[Quantity, Unit("meter / second")],
        dt: Annotated[Quantity, Unit("second")],
    ) -> Annotated[Quantity, Unit("meter")]:
        return velocity + dt

    with pytest.raises(UnitsCompileError):
        verify(distance_invalid)
