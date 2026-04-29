// RUN: %mlir-opt --load-dialect-plugin=%units_plugin --load-pass-plugin=%units_plugin --pass-pipeline='builtin.module(convert-units-to-arith)' %s | %FileCheck %s

module {
  %0 = units.const 4.2 : !units.quantity<f64, "m">
  %1 = units.const 2.0 : !units.quantity<f64, "s">
  %2 = units.mul %0, %1
    : !units.quantity<f64, "m">, !units.quantity<f64, "s">
    -> !units.quantity<f64, "m*s">

  // CHECK: arith.constant 4.200000e+00 : f64
  // CHECK: arith.constant 2.000000e+00 : f64
  // CHECK: arith.mulf
}
