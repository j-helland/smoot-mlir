// RUN: %units-opt %s -verify-diagnostics

module {
  %0 = units.const 4.2 : !units.quantity<f64, #units.unit<"meter">>
  %1 = units.const 2.0 : !units.quantity<f64, #units.unit<"second">>

  // expected-error @below {{failed to infer result type}}
  %2 = units.add %0, %1
    : !units.quantity<f64, #units.unit<"meter">>, !units.quantity<f64, #units.unit<"second">>
}
