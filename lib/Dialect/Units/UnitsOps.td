include "mlir/IR/OpBase.td"

include "Units/UnitsTypes.td"

class Units_Op<string mnemonic, list<Trait> traits = []>
  : Op<UnitsDialect, mnemonic, traits>;

def Units_ConstOp : Units_Op<"const"> {
  let summary = "constant quantity with a unit annotation";

  let arguments = (ins F64Attr:$value);
  let results = (outs Units_QuantityType:$result);

  // Divert printer and parser to `parse` and `print` methods in the .cpp file.
  let hasCustomAssemblyFormat = 1;

  // Indicate that additional verification is required.
  let hasVerifier = 1;
}

def Units_MulOp : Units_Op<"mul"> {
  let summary = "arithmetic multiplication of quantities";

  let arguments = (ins Units_QuantityType:$lhs, Units_QuantityType:$rhs);
  let results = (outs Units_QuantityType:$result);

  let builders = [
    OpBuilder<(ins "mlir::Value":$lhs, "mlir::Value":$rhs)>
  ];

  let hasCustomAssemblyFormat = 1;
  let hasVerifier = 1;
}

def Units_AddOp : Units_Op<"add"> {
  let summary = "arithmetic addition of quantities";

  let arguments = (ins Units_QuantityType:$lhs, Units_QuantityType:$rhs);
  let results = (outs Units_QuantityType:$result);

  let builders = [
    OpBuilder<(ins "mlir::Value":$lhs, "mlir::Value":$rhs)>
  ];

  let hasCustomAssemblyFormat = 1;
  let hasVerifier = 1;
}
