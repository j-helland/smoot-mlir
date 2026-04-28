// RUN: %mlir-opt --load-dialect-plugin=%units_plugin %s -verify-diagnostics

module {
  // expected-error @below {{unit must not be empty}}
  %0 = units.const 4.2 "" : f64
}

