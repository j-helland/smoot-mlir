from units.ast_parser import transform_ast
import pytest
from syrupy.data import Snapshot

from units import Quantity, Unit, UnitsCompileError
from units.driver import UnitsOpt
from units.mlir_emit import emit_mlir


def test_run_units_opt(snapshot: Snapshot):
    """Happy path."""

    def distance(
        velocity: Quantity[float, Unit("meter / second")],
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
        return velocity * dt

    func_ast = transform_ast(distance)
    units_mlir = emit_mlir(func_ast)
    units_opt = UnitsOpt.default()
    mlir = units_opt.run_units_opt(units_mlir)

    assert mlir == snapshot


def test_run_units_opt_invalid():
    """Verify that the compiler backend fails on an invalid computation."""

    def distance_invalid(
        velocity: Quantity[float, Unit("meter / second")],
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
        return velocity + dt

    func_ast = transform_ast(distance_invalid)
    units_mlir = emit_mlir(func_ast)
    units_opt = UnitsOpt.default()

    with pytest.raises(UnitsCompileError):
        units_opt.run_units_opt(units_mlir)


def test_run_units_opt_not_mlir():
    units_opt = UnitsOpt.default()
    with pytest.raises(UnitsCompileError):
        units_opt.run_units_opt("hello")
