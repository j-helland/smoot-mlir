include "mlir/IR/OpBase.td"
include "Units/UnitsDialect.td"

class Units_Op<string mnemonic, list<Trait> traits = []>
  : Op<UnitsDialect, mnemonic, traits>;

def Units_ConstOp : Units_Op<"const"> {
  let summary = "constant quantity with a unit annotation";

  let arguments = (ins F64Attr:$value, StrAttr:$unit);
  let results = (outs F64:$result);
}
