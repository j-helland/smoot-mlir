from units import Quantity, Unit
from units.ast_parser import lower_function
from units.ir import Binary, Name, Operator


def test_lower_return_mul():
    def distance(
        velocity: Quantity[float, Unit("meter / second")],
        dt: Quantity[float, Unit("second")],
    ) -> Quantity[float, Unit("meter")]:
        return velocity * dt

    fn = lower_function(distance)

    assert isinstance(fn.body.value, Binary)
    assert fn.body.value.op == Operator.mul
    assert fn.body.value.type.unit.dims == (1,)
    assert isinstance(fn.body.value.lhs, Name)
    assert fn.body.value.lhs.name == "velocity"
    assert isinstance(fn.body.value.rhs, Name)
    assert fn.body.value.rhs.name == "dt"
