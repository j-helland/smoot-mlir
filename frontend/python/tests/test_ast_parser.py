from units import Quantity, Unit
from units.ast_parser import lower_function
from units.ir import Binary, Name, Operator, Return


def test_lower_return_mul():
    def distance(
        velocity: Quantity[float, Unit("meter / second")],
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
        return velocity * dt

    fn = lower_function(distance)

    body, *others = fn.body
    assert not others
    assert isinstance(body, Return)
    assert isinstance(body.expr, Binary)
    assert body.expr.op == Operator.mul
    assert body.expr.type.unit.dims == (1,)
    assert isinstance(body.expr.lhs, Name)
    assert body.expr.lhs.name == "velocity"
    assert isinstance(body.expr.rhs, Name)
    assert body.expr.rhs.name == "dt"

    assert fn.span is not None
    assert fn.span.line == 7
    assert fn.span.end_line == 11
