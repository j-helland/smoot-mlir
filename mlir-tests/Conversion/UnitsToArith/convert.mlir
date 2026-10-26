// RUN: %units-opt --pass-pipeline='builtin.module(units-to-standard)' %s | %FileCheck %s

!meters = !units.quantity<f64, #units.unit<"meter">>
!centimeters = !units.quantity<f64, #units.unit<"centimeter">>

module {
  // CHECK-LABEL: func.func @meters_to_centimeters(
  // CHECK-SAME: %[[X:[a-zA-Z0-9_]+]]: f64) -> f64
  func.func @meters_to_centimeters(%x: !meters) -> !centimeters {
    // CHECK: %[[FACTOR:[a-zA-Z0-9_]+]] = arith.constant 1.000000e+02 : f64
    // CHECK-NEXT: %[[RESULT:[a-zA-Z0-9_]+]] = arith.mulf %[[X]], %[[FACTOR]] : f64
    %converted = units.convert %x : !meters to !centimeters

    // CHECK-NEXT: return %[[RESULT]] : f64
    func.return %converted : !centimeters
  }
}
