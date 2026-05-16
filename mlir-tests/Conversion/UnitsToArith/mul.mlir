// RUN: %units-opt --pass-pipeline='builtin.module(units-to-standard)' %s | %FileCheck %s

module {
  %0 = units.const 4.2 : !units.quantity<f64, #units.unit<"meter">>
  %1 = units.const 2.0 : !units.quantity<f64, #units.unit<"second">>
  %2 = units.mul %0, %1
    : !units.quantity<f64, #units.unit<"meter">>, !units.quantity<f64, #units.unit<"second">>

  // CHECK: arith.constant 4.200000e+00 : f64
  // CHECK: arith.constant 2.000000e+00 : f64
  // CHECK: arith.mulf
}
