from types import FunctionType
from typing import Annotated

import pytest

from units import Quantity, Unit
from units.ast_parser import transform_ast
from units.mlir_emit import emit_mlir

type Meter = Annotated[Quantity, Unit("meter")]
type Centimeter = Annotated[Quantity, Unit("centimeter")]
type Second = Annotated[Quantity, Unit("second")]
type MetersPerSecond = Annotated[Quantity, Unit("meter / second")]


def func_mul(velocity: MetersPerSecond, dt: Second) -> Meter:
    return velocity * dt


def func_add(x: Meter, y: Meter) -> Meter:
    return x + y


def func_multi_argument(x: Meter, v: MetersPerSecond, dt: Second) -> Meter:
    dx = v * dt
    pos = x + dx
    return pos


def func_for_loop_range(x: Meter) -> Meter:
    for _ in range(3):
        x = x + x
    return x


def func_for_loop_range_with_step(x: Meter) -> Meter:
    for _ in range(1, 5, 2):
        x = x + x
    return x


def func_for_loop_range_with_target(x: Meter) -> Meter:
    for i in range(10):
        x = x + x
    return x


def func_meter_to_centimeter(x: Meter) -> Centimeter:
    return x.to("cm")


@pytest.mark.parametrize(
    "func",
    (
        func_mul,
        func_add,
        func_multi_argument,
        func_for_loop_range,
        func_for_loop_range_with_step,
        func_for_loop_range_with_target,
        func_meter_to_centimeter,
    ),
)
def test_mlir_emitter(func: FunctionType, snapshot: object):
    fn = transform_ast(func)
    mlir = emit_mlir(fn)

    assert str(mlir) == snapshot
