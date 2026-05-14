from typing import Callable
import pytest
from units import Quantity, Unit
from units.ast_parser import lower_function
from units.mlir_emit import emit_module


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
def test_mlir_emitter(func: Callable, snapshot: object):
    fn = lower_function(func)
    mlir = emit_module(fn)

    assert mlir == snapshot
