from __future__ import annotations

from units.diagnostics import UnitsCompileError

import functools
from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    TypeAlias,
    get_args,
    get_origin,
)

Dimensionality: TypeAlias = tuple[int, ...]


@dataclass(frozen=True)
class QuantityTypeInfo:
    element: str
    unit: Unit


@dataclass(frozen=True)
class Unit:
    expression: str


@dataclass(frozen=True)
class QuantityAnnotation:
    element_type: type
    unit: Unit

    @classmethod
    def from_params(cls, params: Any) -> QuantityAnnotation:
        if not isinstance(params, tuple) or len(params) != 2:
            msg = "units.Quantity[...] expects two parameters: element type and unit expression string"
            raise UnitsCompileError(msg)

        element_type, unit = params
        if element_type is not float:
            msg = f"only units.Quantity[float, ...] is supported for now, got `{element_type!r}`"
            raise UnitsCompileError(msg)
        if not isinstance(unit, Unit):
            msg = f"unit expression parameter must be a Unit type, got `{type(unit)}`"
            raise UnitsCompileError(msg)

        return cls(
            element_type=element_type,
            unit=unit,
        )

    def to_info(self) -> QuantityTypeInfo:
        return parse_quantity_annotation(self)


@functools.singledispatch
def parse_quantity_annotation(annotation: Any) -> QuantityTypeInfo:
    if get_origin(annotation) is not Annotated:
        msg = f"Unsupported quantity annotation type {type(annotation)!r}. Expected Quantity[...] or Annotated[...]."
        raise UnitsCompileError(msg)

    (
        element_type,
        unit,
        *metadata,
    ) = get_args(annotation)

    if metadata:
        msg = "Annotated quantity must include exactly one Unit(...)"
        raise UnitsCompileError(msg)

    return QuantityTypeInfo(
        element=_parse_element_type(element_type),
        unit=_parse_unit_type(unit),
    )


@parse_quantity_annotation.register
def _(annotation: QuantityAnnotation) -> QuantityTypeInfo:
    return QuantityTypeInfo(
        element=_parse_element_type(annotation.element_type),
        unit=annotation.unit,
    )


def _parse_element_type(element: type) -> str:
    # TODO(jwh): mocked type support for now
    if element is float:
        return "f64"

    msg = "Only float quantities are supported for now"
    raise UnitsCompileError(msg) from NotImplementedError


@functools.singledispatch
def _parse_unit_type(unit: Any) -> Unit:
    msg = f"cannot interpret {unit!r} with type {type(unit)} as a unit"
    raise UnitsCompileError(msg)


@_parse_unit_type.register
def _(unit: str) -> Unit:
    return Unit(unit)


@_parse_unit_type.register
def _(unit: Unit) -> Unit:
    return unit
