#ifndef LIB_DIALECT_UNITS_UNITSTYPES_TD_
#define LIB_DIALECT_UNITS_UNITSTYPES_TD_

include "mlir/IR/AttrTypeBase.td"
include "Units/UnitsDialect.td"
include "Units/UnitsAttrs.td"

def Units_QuantityType : TypeDef<UnitsDialect, "Quantity"> {
    let mnemonic = "quantity";
    let summary = "physical quantity type";

    let parameters = (ins
        "mlir::Type":$elementType,
        TypeParameter<"::mlir::units::UnitAttr", "unit attribute">:$unit
    );

    let hasCustomAssemblyFormat = 1;
}

#endif  // LIB_DIALECT_UNITS_UNITSTYPES_TD_
