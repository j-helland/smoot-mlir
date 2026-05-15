from __future__ import annotations

from typing import TYPE_CHECKING

from .annotations import QuantityAnnotation, Unit
from .errors import UnitsCompileError
from .verify import verify

if TYPE_CHECKING:
    from typing import Any


class Quantity:
    """TODO(jwh): document"""

    def __class_getitem__(cls, params: Any) -> QuantityAnnotation:
        return QuantityAnnotation.from_params(params)

    def __mul__(self, other: Any) -> Quantity:
        raise NotImplementedError

    def __add__(self, other: Any) -> Quantity:
        raise NotImplementedError


__all__ = [
    # verify
    "Quantity",
    "Unit",
    "verify",
    # errors
    "UnitsCompileError",
]
