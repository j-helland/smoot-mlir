from typing import Annotated

import pytest
from syrupy.assertion import SnapshotAssertion

from units import Quantity, Unit, UnitsCompileError
from units.ast_parser import transform_ast
from units.ir import (
    Assign,
    Binary,
    Constant,
    For,
    Function,
    Name,
    Operator,
    Range,
    Return,
)

type Meters = Annotated[Quantity, Unit("meter")]
type Second = Annotated[Quantity, Unit("second")]
type MetersPerSecond = Annotated[Quantity, Unit("meter / second")]


def test_transform_return_mul():
    def distance(velocity: MetersPerSecond, dt: Second) -> Meters:
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
    def f(x: Meters) -> Meters:
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
    def f() -> Meters:
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
        x: Meters = source
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


def test_transform_for_range():
    def repeat(x: Meters) -> Meters:
        for _ in range(3):
            x = x + x
        return x

    func = transform_ast(repeat)
    assert isinstance(func, Function)

    loop, result = func.body
    assert isinstance(loop, For)
    assert isinstance(loop.iterable, Range)

    bounds = loop.iterable
    assert isinstance(bounds.start, Constant)
    assert bounds.start.value == 0
    assert isinstance(bounds.stop, Constant)
    assert bounds.stop.value == 3
    assert isinstance(bounds.step, Constant)
    assert bounds.step.value == 1

    assert len(loop.body) == 1
    assert isinstance(loop.body[0], Assign)
    assert loop.body[0].name == "x"
    assert isinstance(result, Return)
