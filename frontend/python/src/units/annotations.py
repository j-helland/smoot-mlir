from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin

import typing_extensions

from units.diagnostics import Diagnostic, UnitsCompileError
from units.quantity import Quantity, Unit
from units.span import SourceSpan


@dataclass(frozen=True)
class QuantityTypeInfo:
    element: str
    unit: Unit


def parse_quantity_annotation(
    annotation: Any,
    span: SourceSpan | None = None,
) -> QuantityTypeInfo:
    while isinstance(annotation, typing_extensions.TypeAliasType):
        annotation = annotation.__value__

    if get_origin(annotation) is not Annotated:
        msg = f'Unsupported quantity annotation {annotation!r}. Expected Annotated[Quantity, Unit("...")].'
        raise UnitsCompileError(Diagnostic.frontend(msg, span))

    quantity_type, unit, *metadata = get_args(annotation)

    if metadata:
        msg = "Annotated quantity must include exactly one Unit(...)"
        raise UnitsCompileError(Diagnostic.frontend(msg, span))

    while isinstance(quantity_type, typing_extensions.TypeAliasType):
        quantity_type = quantity_type.__value__

    if get_origin(quantity_type) is Quantity:
        (quantity_type,) = get_args(quantity_type)
    if quantity_type not in (Quantity, float):
        msg = "Only float quantities are supported for now"
        raise UnitsCompileError(Diagnostic.frontend(msg, span))

    if isinstance(unit, str):
        unit = Unit(unit)
    if not isinstance(unit, Unit):
        msg = f"cannot interpret {unit!r} as a unit"
        raise UnitsCompileError(Diagnostic.frontend(msg, span))

    return QuantityTypeInfo(element="f64", unit=unit)
