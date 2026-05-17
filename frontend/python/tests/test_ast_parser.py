import pytest
from syrupy.assertion import SnapshotAssertion

from units import Quantity, Unit, UnitsCompileError
from units.ast_parser import transform_ast
from units.ir import Assign, Binary, Constant, Function, Name, Operator, Return


def test_transform_return_mul():
    def distance(
        velocity: Quantity[float, Unit("meter / second")],
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
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
    def f(x: Quantity[float, Unit("meter")]) -> Quantity[float, Unit("meter")]:
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
    def f() -> Quantity[float, Unit("meter")]:
        # annotated assigment
        x: Quantity[float, Unit("meter")] = 1.0
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
    def f() -> Quantity[float, Unit("meter")]:
        return distance  # noqa: F821  # ty:ignore[unresolved-reference]

    _check_rendered_compile_error(f, diagnostic_snapshot)


def _check_rendered_compile_error(
    code: object,
    diagnostic_snapshot: SnapshotAssertion,
) -> None:
    with pytest.raises(UnitsCompileError) as exc_info:
        transform_ast(code)

    diagnostic_snapshot.assert_match(str(exc_info.value))
