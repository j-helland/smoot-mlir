// RUN: %units-opt %s -verify-diagnostics

module {
  %0 = units.const 4.2 : !units.quantity<f64, #units.unit<dims = [1]>>
  %1 = units.const 2.0 : !units.quantity<f64, #units.unit<dims = [0, 1]>>

  // expected-error @below {{operand units must match}}
  %2 = units.add %0, %1
    : !units.quantity<f64, #units.unit<dims = [1]>>, !units.quantity<f64, #units.unit<dims = [0, 1]>>
    -> !units.quantity<f64, #units.unit<dims = [1]>>
}
