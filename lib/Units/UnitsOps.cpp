#include "Units/UnitsOps.h"
#include "Units/UnitsTypes.h"

// For `let hasCustomAssemblyFormat = 1`
mlir::ParseResult units::ConstOp::parse(mlir::OpAsmParser &parser,
                                        mlir::OperationState &result) {
  double value;
  mlir::Type resultType;

  if (parser.parseFloat(value))
    return mlir::failure();

  auto typeLoc = parser.getCurrentLocation();
  if (parser.parseColonType(resultType))
    return mlir::failure();

  auto quantityType = llvm::dyn_cast<units::QuantityType>(resultType);
  if (!quantityType)
    return parser.emitError(typeLoc) << "result must be a quantity type";

  auto elementType =
      llvm::dyn_cast<mlir::FloatType>(quantityType.getElementType());
  if (!elementType)
    return parser.emitError(typeLoc) << "expected floating-point result type";

  result.addAttribute(
      "value", mlir::FloatAttr::get(quantityType.getElementType(), value));
  result.addTypes(resultType);
  return mlir::success();
}

// For `let hasCustomAssemblyFormat = 1`
/**
 * # Examples
 * ```
 * module {
 *   %0 = units.const 4.200000e+00 "m" : f64
 * }
 * ```
 */
void units::ConstOp::print(mlir::OpAsmPrinter &printer) {
  // only print the float value, otherwise we get redundant `f64`s.
  printer << " " << getValueAttr().getValueAsDouble();
  printer << " : ";
  printer.printType(getResult().getType());
}

// For `let hasVerifier = 1`
llvm::LogicalResult units::ConstOp::verify() {
  auto resultType = llvm::dyn_cast<units::QuantityType>(getResult().getType());
  if (!resultType)
    return emitOpError() << "result must be a quantity type";

  if (resultType.getUnit().empty())
    return emitOpError() << "unit must not be empty";

  if (getValueAttr().getType() != resultType.getElementType())
    return emitOpError() << "value attribute type must match result type";

  return mlir::success();
}

//==================================================
// TableGen'd op method definitions
//==================================================
#define GET_OP_CLASSES
#include "Units/UnitsOps.cpp.inc"
