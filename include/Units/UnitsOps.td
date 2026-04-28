include "mlir/IR/OpBase.td"
include "Units/UnitsDialect.td"

class Units_Op<string mnemonic, list<Trait> traits = []>
  : Op<UnitsDialect, mnemonic, traits>;

def Units_ConstOp : Units_Op<"const"> {
  let summary = "constant quantity with a unit annotation";

  let arguments = (ins F64Attr:$value, StrAttr:$unit);
  let results = (outs F64:$result);

  // Divert printer and parser to `parse` and `print` methods in the .cpp file.
  let hasCustomAssemblyFormat = 1;

  // Indicate that additional verification is required.
  let hasVerifier = 1;
}
