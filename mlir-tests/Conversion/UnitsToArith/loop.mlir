// RUN: %units-opt --pass-pipeline='builtin.module(units-to-standard)' %s | %FileCheck %s

!length = !units.quantity<f64, #units.unit<"meter">>
!velocity = !units.quantity<f64, #units.unit<"meter / second">>
!time = !units.quantity<f64, #units.unit<"second">>

module {

  // CHECK-LABEL: func.func @integrate(
  // CHECK-SAME: %[[X:[a-zA-Z0-9_]+]]: f64,
  // CHECK-SAME: %[[V:[a-zA-Z0-9_]+]]: f64,
  // CHECK-SAME: %[[DT:[a-zA-Z0-9_]+]]: f64) -> f64

  // CHECK: %[[ZERO:[a-zA-Z0-9_]+]] = arith.constant 0 : index
  // CHECK: %[[ONE:[a-zA-Z0-9_]+]] = arith.constant 1 : index
  // CHECK: %[[COUNT:[a-zA-Z0-9_]+]] = arith.constant 1000 : index

  // CHECK: %[[FINAL:[a-zA-Z0-9_]+]] = scf.for %{{[a-zA-Z0-9_]+}} = %[[ZERO]] to %[[COUNT]] step %[[ONE]]
  // CHECK-SAME: iter_args(%[[CURRENT:[a-zA-Z0-9_]+]] = %[[X]]) -> (f64) {
  // CHECK-NEXT: %[[DX:[a-zA-Z0-9_]+]] = arith.mulf %[[V]], %[[DT]] : f64
  // CHECK-NEXT: %[[NEXT:[a-zA-Z0-9_]+]] = arith.addf %[[CURRENT]], %[[DX]] : f64
  // CHECK-NEXT: scf.yield %[[NEXT]] : f64
  // CHECK-NEXT: }
  // CHECK-NEXT: return %[[FINAL]] : f64
  func.func @integrate(
      %x: !length, %v: !velocity, %dt: !time) -> !length {
    %c0 = arith.constant 0 : index
    %c1 = arith.constant 1 : index
    %count = arith.constant 1000 : index

    %final = scf.for %i = %c0 to %count step %c1
        iter_args(%current = %x) -> (!length) {
      %dx = units.mul %v, %dt : !velocity, !time
      %next = units.add %current, %dx : !length, !length
      scf.yield %next : !length
    }

    func.return %final : !length
  }
}
