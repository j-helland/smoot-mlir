#include "Units/UnitsOps.h"
#include "Units/UnitsTypes.h"
#include "mlir/IR/OpImplementation.h"
#include "llvm/Support/Casting.h"
#include "llvm/Support/LogicalResult.h"

//==================================================
// ConstOp
//==================================================
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
// MulOp
//==================================================
mlir::ParseResult units::MulOp::parse(mlir::OpAsmParser &parser,
                                      mlir::OperationState &result) {
  mlir::OpAsmParser::UnresolvedOperand lhs;
  mlir::OpAsmParser::UnresolvedOperand rhs;
  mlir::Type lhsType;
  mlir::Type rhsType;
  mlir::Type resultType;

  if (parser.parseOperand(lhs) || parser.parseComma() ||
      parser.parseOperand(rhs))
    return mlir::failure();

  if (parser.parseColonType(lhsType) || parser.parseComma() ||
      parser.parseType(rhsType))
    return mlir::failure();

  if (parser.parseArrowTypeList(result.types) ||
      parser.resolveOperand(lhs, lhsType, result.operands) ||
      parser.resolveOperand(rhs, rhsType, result.operands))
    return mlir::failure();

  return mlir::success();
}

void units::MulOp::print(mlir::OpAsmPrinter &printer) {
  printer << " " << getLhs() << ", " << getRhs() << " : ";
  printer.printType(getLhs().getType());
  printer << ", ";
  printer.printType(getRhs().getType());
  printer << " -> ";
  printer.printType(getResult().getType());
}

llvm::LogicalResult units::MulOp::verify() {
  auto lhsType = llvm::cast<units::QuantityType>(getLhs().getType());
  auto rhsType = llvm::cast<units::QuantityType>(getRhs().getType());
  auto resultType = llvm::cast<units::QuantityType>(getResult().getType());

  if (lhsType.getElementType() != rhsType.getElementType() ||
      lhsType.getElementType() != resultType.getElementType())
    return emitOpError() << "operand and result element types must match";

  llvm::StringRef lhsUnit = lhsType.getUnit();
  llvm::StringRef rhsUnit = rhsType.getUnit();
  llvm::StringRef resultUnit = resultType.getUnit();

  // TODO(jwh): temporary PoC
  if (lhsUnit == "m" && rhsUnit == "s") {
    if (resultUnit != "m*s")
      return emitOpError() << "expected result unit `m*s`";
    return mlir::success();
  }

  return emitOpError() << "unsupported unit multiplication `" << lhsUnit
                       << "` * `" << rhsUnit << "`";
}

//==================================================
// TableGen'd op method definitions
//==================================================
#define GET_OP_CLASSES
#include "Units/UnitsOps.cpp.inc"
