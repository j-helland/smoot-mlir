from typing import Annotated, TypeAlias

import pytest
from syrupy.assertion import SnapshotAssertion

from units import Quantity, Unit, UnitsCompileError
from units.ast_parser import transform_ast
from units.ir import Assign, Binary, Constant, Function, Name, Operator, Return

Meters: TypeAlias = Annotated[Quantity[float], Unit("meter")]


def test_transform_return_mul():
    def distance(
        velocity: Annotated[Quantity, Unit("meter / second")],
        dt: Annotated[Quantity, Unit("second")],
    ) -> Annotated[Quantity, Unit("meter")]:
        return velocity * dt

    fn_ast = transform_ast(distance)
    assert isinstance(fn_ast, Function)

    body, *others = fn_ast.body
    assert not others
    assert isinstance(body, Return)
    assert isinstance(body.expr, Binary)
    assert body.expr.op == Operator.mul
    assert isinstance(body.expr.lhs, Name)
    assert body.expr.lhs.name == "velocity"
    assert isinstance(body.expr.rhs, Name)
    assert body.expr.rhs.name == "dt"

    assert fn_ast.span is not None


def test_transform_assignment():
    def f(x: Annotated[Quantity, Unit("meter")]) -> Annotated[Quantity, Unit("meter")]:
        # regular assigment
        y = x
        return y

    fn_ast = transform_ast(f)
    assert isinstance(fn_ast, Function)

    body_assign, body_return, *others = fn_ast.body
    assert not others
    assert isinstance(body_assign, Assign)
    assert body_assign.declared_type is None
    assert body_assign.name == "y"
    assert isinstance(body_assign.expr, Name)
    assert body_assign.expr.name == "x"

    assert isinstance(body_return, Return)
    assert isinstance(body_return.expr, Name)
    assert body_return.expr.name == "y"


def test_transform_annotated_assignment():
    def f() -> Annotated[float, Unit("meter")]:
        # annotated assigment
        x: Annotated[float, Unit("meter")] = 1.0
        return x

    fn_ast = transform_ast(f)
    assert isinstance(fn_ast, Function)

    body_assign, body_return, *others = fn_ast.body
    assert not others
    assert isinstance(body_assign, Assign)
    assert body_assign.declared_type is not None
    assert body_assign.declared_type.element == "f64"
    assert body_assign.declared_type.unit == Unit("meter")
    assert body_assign.name == "x"
    assert isinstance(body_assign.expr, Constant)
    assert body_assign.expr.value == 1.0
    assert body_assign.expr.type is None

    assert isinstance(body_return, Return)
    assert isinstance(body_return.expr, Name)
    assert body_return.expr.name == "x"


def test_transform_invalid(diagnostic_snapshot: SnapshotAssertion):
    def f() -> Annotated[Quantity, Unit("meter")]:
        return distance  # noqa: F821  # ty:ignore[unresolved-reference]

    _check_rendered_compile_error(f, diagnostic_snapshot)


def _check_rendered_compile_error(
    code: object,
    diagnostic_snapshot: SnapshotAssertion,
) -> None:
    with pytest.raises(UnitsCompileError) as exc_info:
        transform_ast(code)

    diagnostic_snapshot.assert_match(str(exc_info.value))


def test_transform_quantity_aliases():
    def f(source: Meters) -> Meters:
        x: Annotated[Quantity[float], Unit("meter")] = source
        y: Meters = x
        return y

    fn_ast = transform_ast(f)
    assert isinstance(fn_ast, Function)
    first, second, _ = fn_ast.body
    assert isinstance(first, Assign)
    assert isinstance(second, Assign)
    assert first.declared_type == second.declared_type
    assert first.declared_type is not None
    assert first.declared_type.element == "f64"
    assert first.declared_type.unit == Unit("meter")
