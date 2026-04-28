// RUN: %mlir-opt --load-dialect-plugin=%units_plugin %s | %FileCheck %s

module {
  %0 = units.const 4.2 : !units.quantity<f64, "m">
  %1 = units.const 4.2 : !units.quantity<f64, "s">

  // CHECK: %[[RES:.*]] = units.mul %[[LHS:.*]], %[[RHS:.*]] : !units.quantity<f64, "m">, !units.quantity<f64, "s"> -> !units.quantity<f64, "m*s">
  %2 = units.mul %0, %1 : !units.quantity<f64, "m">, !units.quantity<f64, "s"> -> !units.quantity<f64, "m*s">
}
