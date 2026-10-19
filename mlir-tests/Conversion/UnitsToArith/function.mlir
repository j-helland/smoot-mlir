// RUN: %units-opt --pass-pipeline='builtin.module(units-to-standard)' %s | %FileCheck %s

!meters = !units.quantity<f64, #units.unit<"meter">>

module {
    // CHECK-LABEL: func.func @double_length(
    // CHECK-SAME: %[[X:[a-zA-Z0-9_]+]]: f64) -> f64
    func.func @double_length(%x: !meters) -> !meters {
        // CHECK: %[[RESULT:[a-zA-Z0-9_]+]] = arith.addf %[[X]], %[[X]] : f64
        %result = units.add %x, %x : !meters, !meters

        // CHECK-NEXT: return %[[RESULT]] : f64
        func.return %result : !meters
    }
}
