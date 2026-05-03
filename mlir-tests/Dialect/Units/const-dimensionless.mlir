// RUN: %units-opt %s -verify-diagnostics | %FileCheck %s

module {
  // CHECK: %{{.*}} = units.const 4.200000e+00 : !units.quantity<f64, #units.unit<dims = []>>
  %0 = units.const 4.2 : !units.quantity<f64, #units.unit<dims = []>>
}
