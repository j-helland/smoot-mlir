from __future__ import annotations

from dataclasses import dataclass
from types import FunctionType
from typing import get_type_hints

from units.annotations import (
    QuantityTypeInfo,
    parse_quantity_annotation,
)


@dataclass(frozen=True)
class FunctionSignature:
    name: str
    parameters: tuple[tuple[str, QuantityTypeInfo], ...]
    result: QuantityTypeInfo

    @classmethod
    def extract(cls, fn: FunctionType) -> FunctionSignature:
        # Fully handle `Annotated[...]` metadata.
        annotations = get_type_hints(fn, include_extras=True)

        params = []
        for name in fn.__code__.co_varnames[: fn.__code__.co_argcount]:
            annotation = annotations.get(name)
            params.append((name, parse_quantity_annotation(annotation)))

        result = parse_quantity_annotation(annotations.get("return"))

        return cls(
            name=fn.__name__,
            parameters=tuple(params),
            result=result,
        )
