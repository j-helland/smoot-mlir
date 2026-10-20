from typing import TYPE_CHECKING, Annotated, assert_type

import pytest

from units import Quantity, Unit, UnitsCompileError
from units.annotations import QuantityTypeInfo, parse_quantity_annotation

if TYPE_CHECKING:

    def _check_quantity_methods(x: Annotated[Quantity, Unit("meter")]) -> None:
        assert_type(x * x, Quantity[float])
        assert_type(x.to("km"), Quantity[float])
        assert_type(x.to(Unit("km")), Quantity[float])


def test_quantity_info_parsing():
    unit = Unit("meter / second")
    assert parse_quantity_annotation(
        Annotated[Quantity[float], unit]
    ) == QuantityTypeInfo(element="f64", unit=unit)

    # The backend validates unit expressions.
    unit = Unit("definitely not a unit expression")
    assert parse_quantity_annotation(Annotated[Quantity, unit]).unit == unit


@pytest.mark.parametrize(
    "annotation",
    (
        Quantity,
        Annotated[Quantity[int], Unit("meter")],
        Annotated[Quantity, Unit("meter"), Unit("second")],
        Annotated[Quantity, 1],
    ),
)
def test_invalid_annotations(annotation: object):
    with pytest.raises(UnitsCompileError):
        parse_quantity_annotation(annotation)
