from units.ast_parser import transform_ast
from units import Quantity, Unit
from units.ir import Binary, Name, Operator, Return, Function


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
    assert body.expr.type.unit.dims == (1,)
    assert isinstance(body.expr.lhs, Name)
    assert body.expr.lhs.name == "velocity"
    assert isinstance(body.expr.rhs, Name)
    assert body.expr.rhs.name == "dt"

    assert fn_ast.span is not None
    assert fn_ast.span.line == 7
    assert fn_ast.span.end_line == 11
