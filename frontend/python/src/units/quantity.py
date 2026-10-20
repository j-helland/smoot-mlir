from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any, Generic

from typing_extensions import TypeVar

ScalarT = TypeVar("ScalarT", default=float)


@dataclass(frozen=True)
class Unit:
    """A unit expression, usable as metadata in ``Annotated`` quantities."""

    expression: str

    def quantity_type(self, element_type: type = float) -> Any:
        """Build an Annotated quantity type for runtime-generated functions."""
        quantity_class: Any = Quantity
        return Annotated[quantity_class[element_type], self]


class Quantity(Generic[ScalarT]):
    """A compiler quantity, defaulting to float, with units in Annotated metadata.

    Operations are compiler intrinsics and cannot be executed as Python yet.
    """

    def __mul__(self, _other: Quantity[ScalarT]) -> Quantity[ScalarT]:
        """Multiply quantities; the compiler computes the resulting units."""
        raise NotImplementedError

    def __add__(self, _other: Quantity[ScalarT]) -> Quantity[ScalarT]:
        """Add quantities; the compiler checks their units are compatible."""
        raise NotImplementedError

    def to(self, unit: str | Unit) -> Quantity[ScalarT]:
        """Return a quantity converted to ``unit``, for example ``x.to("km")``.

        Conversion lowering is not implemented yet.
        """
        raise NotImplementedError
