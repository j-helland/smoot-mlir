// RUN: %units-opt %s | %FileCheck %s

!cm = !units.quantity<f64, #units.unit<"cm">>
!centimeter = !units.quantity<f64, #units.unit<"centimeter">>

module {
  // CHECK-LABEL: func.func @alias_identity(
  // CHECK-SAME: %[[X:[a-zA-Z0-9_]+]]: !units.quantity<f64, #units.unit<"centimeter">>)
  // CHECK-SAME: -> !units.quantity<f64, #units.unit<"centimeter">>
  func.func @alias_identity(%x: !cm) -> !centimeter {
    // CHECK-NEXT: return %[[X]] : !units.quantity<f64, #units.unit<"centimeter">>
    func.return %x : !centimeter
  }
}
