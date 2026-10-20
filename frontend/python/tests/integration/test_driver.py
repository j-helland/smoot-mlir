from typing import Annotated

import pytest

from units import Quantity, Unit, UnitsCompileError
from units.ast_parser import transform_ast
from units.driver import NativeBackend
from units.mlir_emit import emit_mlir

type Meter = Annotated[Quantity, Unit("meter")]
type Second = Annotated[Quantity, Unit("second")]
type MetersPerSecond = Annotated[Quantity, Unit("meter / second")]


def test_verify_happy_path():
    def distance(velocity: MetersPerSecond, dt: Second) -> Meter:
        return velocity * dt

    func_ast = transform_ast(distance)
    units_mlir = emit_mlir(func_ast)

    NativeBackend.default().verify_mlir(units_mlir)


def test_emit_mlir_invalid():
    """Verify that the compiler backend fails on an invalid computation."""

    def distance_invalid(velocity: MetersPerSecond, dt: Second) -> Meter:
        return velocity + dt

    func_ast = transform_ast(distance_invalid)

    with pytest.raises(UnitsCompileError):
        emit_mlir(func_ast)


def test_compile_happy_path():
    def double(x: Meter) -> Meter:
        return x + x

    func_ast = transform_ast(double)
    units_mlir = emit_mlir(func_ast)
    compiled_func = NativeBackend.default().compile_mlir(units_mlir, "double")

    assert compiled_func(2.0) == pytest.approx(4.0)
    assert compiled_func(5.5) == pytest.approx(11.0)
