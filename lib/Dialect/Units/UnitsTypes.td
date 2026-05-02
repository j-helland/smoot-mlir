include "mlir/IR/AttrTypeBase.td"
include "Units/UnitsDialect.td"

def Units_QuantityType : TypeDef<UnitsDialect, "Quantity"> {
  let mnemonic = "quantity";
  let summary = "physical quantity type";

  let parameters = (ins
    "mlir::Type":$elementType,
    StringRefParameter<"unit string">:$unit
  );

  let hasCustomAssemblyFormat = 1;
}
