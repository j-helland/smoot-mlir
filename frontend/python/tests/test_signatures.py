from typing import Annotated
from units import Quantity, Unit
from units.annotations import QuantityTypeInfo, UnitInfo
from units.signatures import FunctionSignature


def test_extract_signature_from_quantity():
    """Verifies function signatures using `Quantity` type annotations."""

    def distance(
        velocity: Quantity[float, Unit("meter / second")],
        # `Annotated` is also supported
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
        return velocity * dt

    sig = FunctionSignature.extract(distance)

    assert sig == FunctionSignature(
        name="distance",
        parameters=(
            ("velocity", QuantityTypeInfo(element="f64", unit=UnitInfo(dims=(1, -1)))),
            ("dt", QuantityTypeInfo(element="f64", unit=UnitInfo(dims=(0, 1)))),
        ),
        result=QuantityTypeInfo(element="f64", unit=UnitInfo(dims=(1,))),
    )


def test_extract_signature_from_annotated():
    """Verifies function signatures using `Annotated` type annotations."""

    def distance(
        # Both `Unit` and `str` are supported in `Annotated` units arg.
        velocity: Annotated[float, Unit("meter / second")],
        dt: Annotated[float, "second"],
    ) -> Annotated[float, "meter"]:
        return velocity * dt

    sig = FunctionSignature.extract(distance)

    assert sig == FunctionSignature(
        name="distance",
        parameters=(
            ("velocity", QuantityTypeInfo(element="f64", unit=UnitInfo(dims=(1, -1)))),
            ("dt", QuantityTypeInfo(element="f64", unit=UnitInfo(dims=(0, 1)))),
        ),
        result=QuantityTypeInfo(element="f64", unit=UnitInfo(dims=(1,))),
    )
