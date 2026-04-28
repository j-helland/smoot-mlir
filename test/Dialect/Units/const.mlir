// RUN: %mlir-opt --load-dialect-plugin=%units_plugin %s | %FileCheck %s

module {
  // CHECK: %{{.*}} = units.const 4.200000e+00 : !units.quantity<f64, "meter">
  %0 = units.const 4.2 : !units.quantity<f64, "meter">
}

