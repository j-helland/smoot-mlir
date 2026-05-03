#ifndef LIB_DIALECT_UNITS_UNITSATTRS_TD_
#define LIB_DIALECT_UNITS_UNITSATTRS_TD_

include "mlir/IR/AttrTypeBase.td"
include "Units/UnitsDialect.td"

def Units_UnitAttr : AttrDef<UnitsDialect, "Unit"> {
    let mnemonic = "unit";
    let summary = "canonical physical unit attribute";

    let parameters = (ins
        ArrayRefParameter<"int64_t">:$dims
    );

    let builders = [
        AttrBuilder<(ins "llvm::ArrayRef<int64_t>":$dims), [{
            llvm::SmallVector<int64_t> canonicalDims(dims.begin(), dims.end());
            while (!canonicalDims.empty() && canonicalDims.back() == 0) {
                canonicalDims.pop_back();
            }
            return $_get($_ctxt, canonicalDims);
        }]>
    ];

    let genAccessors = 1;
    let skipDefaultBuilders = 1;
    let hasCustomAssemblyFormat = 1;
}

#endif  // LIB_DIALECT_UNITS_UNITSATTRS_TD_
