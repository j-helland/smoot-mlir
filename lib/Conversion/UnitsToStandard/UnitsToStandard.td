#ifndef LIB_CONVERSION_UNITSTOSTANDARD_UNITSTOSTANDARD_TD_
#define LIB_CONVERSION_UNITSTOSTANDARD_UNITSTOSTANDARD_TD_

include "mlir/Pass/PassBase.td"

def UnitsToStandard : Pass<"units-to-standard"> {
  let summary = "Lower `units` to standard MLIR dialects.";

  let description = [{
    This pass lowers the `units` dialect to standard MLIR.
  }];
  let dependentDialects = [
    "mlir::units::UnitsDialect",
    "mlir::arith::ArithDialect",
    "mlir::scf::SCFDialect",
  ];
}

#endif  // LIB_CONVERSION_UNITSTOSTANDARD_UNITSTOSTANDARD_TD_
