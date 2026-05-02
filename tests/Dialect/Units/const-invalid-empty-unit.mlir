// RUN: %units-opt %s -verify-diagnostics

module {
  // expected-error @below {{unit must not be empty}}
  %0 = units.const 4.2 : !units.quantity<f64, "">
}
