from mlir import ir

from units import _units_backend


def test_register_units_dialect():
    with ir.Context() as ctx:
        _units_backend.register_dialect(ctx)

        text = """!units.quantity<f64, #units.unit<"meter">>"""
        quantity = ir.Type.parse(text)

        assert str(quantity) == text
