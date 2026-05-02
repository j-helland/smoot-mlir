// RUN: %units-opt --pass-pipeline='builtin.module(units-to-standard)' %s | %FileCheck %s

module {
  %0 = units.const 4.2 : !units.quantity<f64, "m">
  %1 = units.const 2.0 : !units.quantity<f64, "m">
  %2 = units.add %0, %1
    : !units.quantity<f64, "m">, !units.quantity<f64, "m">
    -> !units.quantity<f64, "m">

  // CHECK: arith.constant 4.200000e+00 : f64
  // CHECK: arith.constant 2.000000e+00 : f64
  // CHECK: arith.addf
}
