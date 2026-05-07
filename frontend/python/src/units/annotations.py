from __future__ import annotations

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
class UnitInfo:
    dims: Dimensionality


@dataclass(frozen=True)
class QuantityTypeInfo:
    element: str
    unit: UnitInfo


@dataclass(frozen=True)
class Unit:
    expression: str

    def to_info(self) -> UnitInfo:
        return _parse_unit_expr(self.expression)


@dataclass(frozen=True)
class QuantityAnnotation:
    element_type: type
    unit: Unit

    @classmethod
    def from_params(cls, params: Any) -> QuantityAnnotation:
        if not isinstance(params, tuple) or len(params) != 2:
            msg = "units.Quantity[...] expects two parameters: element type and unit expression string"
            raise TypeError(msg)

        element_type, unit = params
        if element_type is not float:
            msg = f"only units.Quantity[float, ...] is supported for now, got `{element_type!r}`"
            raise TypeError(msg)
        if not isinstance(unit, Unit):
            msg = f"unit expression parameter must be a Unit type, got `{type(unit)}`"
            raise TypeError(msg)

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
        raise TypeError(msg)

    (
        element_type,
        unit_type,
        *metadata,
    ) = get_args(annotation)

    if metadata:
        msg = "Annotated quantity must include exactly one Unit(...)"
        raise TypeError(msg)

    return QuantityTypeInfo(
        element=_parse_element_type(element_type),
        unit=_parse_unit_type(unit_type),
    )


@parse_quantity_annotation.register
def _(annotation: QuantityAnnotation) -> QuantityTypeInfo:
    return QuantityTypeInfo(
        element=_parse_element_type(annotation.element_type),
        unit=annotation.unit.to_info(),
    )


def _parse_element_type(element: type) -> str:
    # TODO(jwh): mocked type support for now
    if element is float:
        return "f64"

    msg = "Only float quantities are supported for now"
    raise NotImplementedError(msg) from TypeError(type(element))


@functools.singledispatch
def _parse_unit_type(unit: Any) -> UnitInfo:
    msg = f"Cannot interpret {unit!r} with type {type(unit)} as a unit"
    raise TypeError(msg)


@_parse_unit_type.register
def _(unit: str) -> UnitInfo:
    return _parse_unit_expr(unit)


@_parse_unit_type.register
def _(unit: Unit) -> UnitInfo:
    return unit.to_info()


def _parse_unit_expr(expression: str) -> UnitInfo:
    # TODO(jwh): mocked parser for now
    mapping: dict[str, Dimensionality] = {
        "meter": (1,),
        "second": (0, 1),
        "meter / second": (1, -1),
        "dimensionless": (),
    }

    if (dims := mapping.get(expression)) is None:
        msg = f"unsupported unit expression {expression!r}"
        raise TypeError(msg) from None

    return UnitInfo(dims=dims)
