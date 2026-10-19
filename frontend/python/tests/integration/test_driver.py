from typing import Annotated, TypeAlias

import pytest
from units import Quantity, Unit, UnitsCompileError
from units.ast_parser import transform_ast
from units.driver import NativeBackend
from units.mlir_emit import emit_mlir

Meter: TypeAlias = Annotated[Quantity, Unit("meter")]
Second: TypeAlias = Annotated[Quantity, Unit("second")]
MetersPerSecond: TypeAlias = Annotated[Quantity, Unit("meter / second")]


def test_verify_happy_path():
    def distance(velocity: MetersPerSecond, dt: Second) -> Meter:
        return velocity * dt

    func_ast = transform_ast(distance)
    units_mlir = emit_mlir(func_ast)

    NativeBackend.default().verify_mlir(units_mlir)


def test_verify_invalid():
    """Verify that the compiler backend fails on an invalid computation."""

    def distance_invalid(velocity: MetersPerSecond, dt: Second) -> Meter:
        return velocity + dt

    func_ast = transform_ast(distance_invalid)
    units_mlir = emit_mlir(func_ast)

    with pytest.raises(UnitsCompileError):
        NativeBackend.default().verify_mlir(units_mlir)


def test_verify_not_mlir():
    with pytest.raises(UnitsCompileError):
        NativeBackend.default().verify_mlir("hello")


def test_compile_happy_path():
    def double(x: Meter) -> Meter:
        return x + x

    func_ast = transform_ast(double)
    units_mlir = emit_mlir(func_ast)
    compiled_func = NativeBackend.default().compile_mlir(units_mlir, "double")

    assert compiled_func(2.0) == pytest.approx(4.0)
    assert compiled_func(5.5) == pytest.approx(11.0)


def test_compile_not_mlir():
    with pytest.raises(UnitsCompileError):
        NativeBackend.default().compile_mlir("hello", "func")
