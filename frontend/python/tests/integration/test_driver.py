import pytest

from units import Quantity, Unit, UnitsCompileError
from units.ast_parser import transform_ast
from units.driver import NativeBackend
from units.mlir_emit import emit_mlir


def test_run_backend_happy_path():
    def distance(
        velocity: Quantity[float, Unit("meter / second")],
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
        return velocity * dt

    func_ast = transform_ast(distance)
    units_mlir = emit_mlir(func_ast)

    NativeBackend.default().verify_mlir(units_mlir)


def test_run_units_opt_invalid():
    """Verify that the compiler backend fails on an invalid computation."""

    def distance_invalid(
        velocity: Quantity[float, Unit("meter / second")],
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
        return velocity + dt

    func_ast = transform_ast(distance_invalid)
    units_mlir = emit_mlir(func_ast)

    with pytest.raises(UnitsCompileError):
        NativeBackend.default().verify_mlir(units_mlir)


def test_run_units_opt_not_mlir():
    with pytest.raises(UnitsCompileError):
        NativeBackend.default().verify_mlir("hello")
