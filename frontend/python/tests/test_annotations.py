import pytest

from units import Quantity, Unit
from units.annotations import QuantityAnnotation, QuantityTypeInfo


def test_annotation_instantiation():
    annotation = Quantity[float, Unit("meter / second")]
    assert annotation == QuantityAnnotation(
        element_type=float,
        unit=Unit("meter / second"),
    )

    # Only supports specific quantity value types.
    with pytest.raises(TypeError):
        Quantity[int, Unit("meter / second")]

    # Only supports `Unit` types.
    with pytest.raises(TypeError, match="must be a Unit type"):
        Quantity[float, "meter"]

    # Accepts any expression at annotation instantiation time.
    Quantity[float, Unit("definitely not a unit expression")]


def test_quantity_info_parsing():
    annotation = Quantity[float, Unit("meter / second")]
    info = annotation.to_info()
    assert info == QuantityTypeInfo(
        element="f64",
        unit=Unit("meter / second"),
    )

    # The frontend does not perform typechecking / type inference.
    annotation = Quantity[float, Unit("definitely not a unit expression")]
    info = annotation.to_info()
    assert info == QuantityTypeInfo(
        element="f64",
        unit=Unit("definitely not a unit expression"),
    )
