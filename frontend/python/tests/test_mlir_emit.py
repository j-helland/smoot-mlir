from units.ast_parser import transform_ast
from types import FunctionType

import pytest

from units import Quantity, Unit
from units.mlir_emit import emit_mlir


def func_mul(
    velocity: Quantity[float, Unit("meter / second")],
    dt: Quantity[float, Unit("second")],
) -> Quantity[float, Unit("meter")]:
    return velocity * dt


def func_add(
    x: Quantity[float, Unit("meter")],
    y: Quantity[float, Unit("meter")],
) -> Quantity[float, Unit("meter")]:
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

    assert mlir == snapshot
