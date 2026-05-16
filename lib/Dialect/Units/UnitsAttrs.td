#ifndef LIB_DIALECT_UNITS_UNITSATTRS_TD_
#define LIB_DIALECT_UNITS_UNITSATTRS_TD_

include "mlir/IR/AttrTypeBase.td"
include "Units/UnitsDialect.td"

def Units_UnitAttr : AttrDef<UnitsDialect, "Unit"> {
  let mnemonic = "unit";
  let summary = "canonical physical unit attribute";

  let parameters = (ins StringRefParameter<"unit expresion">:$expression);

  let builders = [AttrBuilder<(ins "llvm::StringRef":$expression), [{
            return $_get($_ctxt, expression);
        }]>];

  let genAccessors = 1;
  let skipDefaultBuilders = 1;
  let hasCustomAssemblyFormat = 1;
}

#endif // LIB_DIALECT_UNITS_UNITSATTRS_TD_
