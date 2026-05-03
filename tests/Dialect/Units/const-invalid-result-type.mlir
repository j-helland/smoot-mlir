// RUN: %units-opt %s -verify-diagnostics

module {
  // expected-error @below {{expected floating-point result type}}
  %0 = units.const 4.2 : !units.quantity<i32, #units.unit<dims = [1]>>
}
