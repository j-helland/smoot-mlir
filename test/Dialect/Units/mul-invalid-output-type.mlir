// RUN: %mlir-opt --load-dialect-plugin=%units_plugin %s -verify-diagnostics

module {
  %0 = units.const 4.2 : !units.quantity<f64, "m">
  %1 = units.const 2.0 : !units.quantity<f64, "s">

  // expected-error @below {{expected result unit `m*s`}}
  %2 = units.mul %0, %1
    : !units.quantity<f64, "m">, !units.quantity<f64, "s">
    -> !units.quantity<f64, "m">
}

