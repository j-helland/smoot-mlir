from types import FunctionType
from typing import Annotated

import pytest

from units import Quantity, Unit
from units.ast_parser import transform_ast
from units.mlir_emit import emit_mlir


def func_mul(
    velocity: Annotated[Quantity, Unit("meter / second")],
    dt: Annotated[Quantity, Unit("second")],
) -> Annotated[Quantity, Unit("meter")]:
    return velocity * dt


def func_add(
    x: Annotated[Quantity, Unit("meter")],
    y: Annotated[Quantity, Unit("meter")],
) -> Annotated[Quantity, Unit("meter")]:
    return x + y


@pytest.mark.parametrize(
    "func",
    (
        func_mul,
        func_add,
    ),
)
def test_mlir_emitter(func: FunctionType, snapshot: object):
    fn = transform_ast(func)
    mlir = emit_mlir(fn)

    assert mlir.text == snapshot
