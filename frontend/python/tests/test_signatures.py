from typing import Annotated

from units import Quantity, Unit
from units.annotations import QuantityTypeInfo
from units.signatures import FunctionSignature


def test_extract_signature_from_quantity():
    """Verifies function signatures using `Quantity` type annotations."""

    def distance(
        velocity: Annotated[Quantity, Unit("meter / second")],
        dt: Annotated[Quantity, Unit("second")],
    ) -> Annotated[Quantity, Unit("meter")]:
        return velocity * dt

    sig = FunctionSignature.extract(distance)

    assert sig == FunctionSignature(
        name="distance",
        parameters=(
            ("velocity", QuantityTypeInfo(element="f64", unit=Unit("meter / second"))),
            ("dt", QuantityTypeInfo(element="f64", unit=Unit("second"))),
        ),
        result=QuantityTypeInfo(element="f64", unit=Unit("meter")),
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
            ("velocity", QuantityTypeInfo(element="f64", unit=Unit("meter / second"))),
            ("dt", QuantityTypeInfo(element="f64", unit=Unit("second"))),
        ),
        result=QuantityTypeInfo(element="f64", unit=Unit("meter")),
    )


def test_extract_signature_from_runtime_annotations():
    unit = Unit("meter")
    annotation = unit.quantity_type()

    def identity(x: annotation) -> annotation:
        return x

    assert FunctionSignature.extract(identity) == FunctionSignature(
        name="identity",
        parameters=(("x", QuantityTypeInfo(element="f64", unit=unit)),),
        result=QuantityTypeInfo(element="f64", unit=unit),
    )
