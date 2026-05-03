#include "Units/UnitsOps.h"
#include "Units/UnitsTypes.h"
#include "mlir/IR/Builders.h"
#include "mlir/IR/OpImplementation.h"
#include "llvm/Support/Casting.h"
#include "llvm/Support/LogicalResult.h"
#include <algorithm>

namespace units = mlir::units;

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

  auto valueAttr = mlir::FloatAttr::get(elementType, llvm::APFloat(value));
  result.addAttribute("value", valueAttr);
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

static units::UnitAttr combineUnits(units::UnitAttr const &lhs,
                                    units::UnitAttr const &rhs) {

  const auto lhsDims = lhs.getDims();
  const auto rhsDims = rhs.getDims();

  const size_t size = std::max(lhsDims.size(), rhsDims.size());
  llvm::SmallVector<int64_t> result;
  result.reserve(size);

  for (size_t i = 0; i < size; ++i) {
    const int64_t lhsDim = i < lhsDims.size() ? lhsDims[i] : 0;
    const int64_t rhsDim = i < rhsDims.size() ? rhsDims[i] : 0;
    result.push_back(lhsDim + rhsDim);
  }

  while (!result.empty() && result.back() == 0)
    result.pop_back();

  return units::UnitAttr::get(lhs.getContext(), result);
}

static bool isSameUnit(units::UnitAttr const &lhs, units::UnitAttr const &rhs) {
    const auto lhsDims = lhs.getDims();
    const auto rhsDims = rhs.getDims();

    const size_t size = std::max(lhsDims.size(), rhsDims.size());
    for (size_t i = 0; i < size; ++i) {
        const int64_t lhsDim = i < lhsDims.size() ? lhsDims[i] : 0;
        const int64_t rhsDim = i < rhsDims.size() ? rhsDims[i] : 0;
        if (lhsDim != rhsDim) return false;
    }
    return true;
}

void units::MulOp::build(mlir::OpBuilder &builder, mlir::OperationState &state,
                         mlir::Value lhs, mlir::Value rhs) {
  auto lhsType = llvm::cast<units::QuantityType>(lhs.getType());
  auto rhsType = llvm::cast<units::QuantityType>(rhs.getType());
  auto resultType = units::QuantityType::get(
      builder.getContext(), lhsType.getElementType(),
      combineUnits(lhsType.getUnit(), rhsType.getUnit()));

  state.addOperands({lhs, rhs});
  state.addTypes(resultType);
}

llvm::LogicalResult units::MulOp::verify() {
  auto lhsType = llvm::cast<units::QuantityType>(getLhs().getType());
  auto rhsType = llvm::cast<units::QuantityType>(getRhs().getType());
  auto resultType = llvm::cast<units::QuantityType>(getResult().getType());

  if (lhsType.getElementType() != rhsType.getElementType() ||
      lhsType.getElementType() != resultType.getElementType())
    return emitOpError() << "operand and result element types must match";

  const units::UnitAttr expectedUnit =
      combineUnits(lhsType.getUnit(), rhsType.getUnit());
  if (!isSameUnit(resultType.getUnit(), expectedUnit))
    return emitOpError() << "expected result unit `" << expectedUnit << "`";

  return mlir::success();
}

//==================================================
// AddOp
//==================================================
mlir::ParseResult units::AddOp::parse(mlir::OpAsmParser &parser,
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

void units::AddOp::print(mlir::OpAsmPrinter &printer) {
  printer << " " << getLhs() << ", " << getRhs() << " : ";
  printer.printType(getLhs().getType());
  printer << ", ";
  printer.printType(getRhs().getType());
  printer << " -> ";
  printer.printType(getResult().getType());
}

void units::AddOp::build(mlir::OpBuilder &builder, mlir::OperationState &state,
                         mlir::Value lhs, mlir::Value rhs) {
  auto lhsType = llvm::cast<units::QuantityType>(lhs.getType());
  auto resultType = units::QuantityType::get(
      builder.getContext(), lhsType.getElementType(), lhsType.getUnit());

  state.addOperands({lhs, rhs});
  state.addTypes(resultType);
}

llvm::LogicalResult units::AddOp::verify() {
  auto lhsType = llvm::cast<units::QuantityType>(getLhs().getType());
  auto rhsType = llvm::cast<units::QuantityType>(getRhs().getType());
  auto resultType = llvm::cast<units::QuantityType>(getResult().getType());

  if (lhsType.getElementType() != rhsType.getElementType() ||
      lhsType.getElementType() != resultType.getElementType())
    return emitOpError() << "operand and result element types must match";

  if (lhsType.getUnit() != rhsType.getUnit())
    return emitOpError() << "operand units must match";

  auto expectedUnit = lhsType.getUnit();
  if (resultType.getUnit() != expectedUnit)
    return emitOpError() << "expected result unit `" << expectedUnit << "`";

  return mlir::success();
}

//==================================================
// TableGen'd op method definitions
//==================================================
#define GET_OP_CLASSES
#include "Units/UnitsOps.cpp.inc"
