// RUN: %units-opt %s -verify-diagnostics

module {
  // expected-error @below {{result must be a quantity type}}
  %0 = units.const 4.2 : f64
}
