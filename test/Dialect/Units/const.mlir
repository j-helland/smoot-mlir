// RUN: %mlir-opt --load-dialect-plugin=%units_plugin %s | %FileCheck %s

module {
  // CHECK: %{{.*}} = units.const 4.200000e+00 "meter" : f64
  %0 = units.const 4.2 "meter" : f64

  // CHECK: %{{.*}} = units.const 4.200000e+00 "m/s" : f64
  %1 = units.const 4.2 "m/s" : f64
}

