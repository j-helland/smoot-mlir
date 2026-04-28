// RUN: %mlir-opt --load-dialect-plugin=%units_plugin %s -verify-diagnostics

module {
  // expected-error @below {{result must be a quantity type}}
  %0 = units.const 4.2 : f64
}
