#include "Units/UnitsOps.h"
#include "Units/UnitsAlgebra.h"
#include "Units/UnitsAttrs.h"
#include "Units/UnitsTypes.h"
#include "mlir/IR/Builders.h"
#include "mlir/IR/MLIRContext.h"
#include "mlir/IR/OpImplementation.h"
#include "llvm/ADT/STLFunctionalExtras.h"
#include "llvm/Support/Casting.h"
#include "llvm/Support/Error.h"
#include "llvm/Support/LogicalResult.h"
#include <mlir/Support/LLVM.h>
#include <cassert>

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

static llvm::FailureOr<units::UnitAttr> applyBinaryUnitOp(
    const units::UnitAttr &lhs, const units::UnitAttr &rhs,
    llvm::function_ref<llvm::Expected<units::algebra::Unit>(
        const units::algebra::Unit &, const units::algebra::Unit &)>
        op) {
  auto lhsUnit = units::algebra::parse(lhs.getExpression());
  if (!lhsUnit) {
    llvm::consumeError(lhsUnit.takeError());
    return llvm::failure();
  }

  auto rhsUnit = units::algebra::parse(rhs.getExpression());
  if (!rhsUnit) {
    llvm::consumeError(rhsUnit.takeError());
    return llvm::failure();
  }

  auto resultUnit = op(*lhsUnit, *rhsUnit);
  if (!resultUnit) {
    llvm::consumeError(resultUnit.takeError());
    return llvm::failure();
  }

  auto resultExpression = units::algebra::format(*resultUnit);
  if (!resultExpression) {
    llvm::consumeError(resultExpression.takeError());
    return llvm::failure();
  }

  return units::UnitAttr::get(lhs.getContext(), *resultExpression);
}

//==================================================
// MulOp
//==================================================
/**
 * Multiply two units together.
 */
static llvm::FailureOr<units::UnitAttr> mulUnits(units::UnitAttr const &lhs,
                                                 units::UnitAttr const &rhs) {
  return applyBinaryUnitOp(lhs, rhs, units::algebra::multiply);
}

/**
 * Infer the return type of a quantity multiplication operation.
 */
static llvm::FailureOr<units::QuantityType>
inferMulResultType(mlir::MLIRContext *context, units::QuantityType lhsType,
                   units::QuantityType rhsType) {
  if (lhsType.getElementType() != rhsType.getElementType())
    return llvm::failure();

  auto resultUnit = mulUnits(lhsType.getUnit(), rhsType.getUnit());
  if (llvm::failed(resultUnit))
    return llvm::failure();

  return units::QuantityType::get(context, lhsType.getElementType(),
                                  *resultUnit);
}

/**
 * Return `true` if two units are equivalent.
 */
static bool isSameUnit(units::UnitAttr const &lhs, units::UnitAttr const &rhs) {
  // TODO(jwh): this is a mock; call out to real units algebra library once.
  return lhs.getExpression() == rhs.getExpression();
}

void units::MulOp::build(mlir::OpBuilder &builder, mlir::OperationState &state,
                         mlir::Value lhs, mlir::Value rhs) {
  auto lhsType = llvm::cast<units::QuantityType>(lhs.getType());
  auto rhsType = llvm::cast<units::QuantityType>(rhs.getType());

  auto resultType = inferMulResultType(builder.getContext(), lhsType, rhsType);
  assert(llvm::succeeded(resultType) &&
         "failed to infer units.mul result type");

  state.addOperands({lhs, rhs});
  state.addTypes(*resultType);
}

mlir::ParseResult units::MulOp::parse(mlir::OpAsmParser &parser,
                                      mlir::OperationState &result) {

  mlir::OpAsmParser::UnresolvedOperand lhs;
  mlir::OpAsmParser::UnresolvedOperand rhs;
  mlir::Type lhsType;
  mlir::Type rhsType;
  mlir::Type resultType;

  auto opLoc = parser.getCurrentLocation();
  if (parser.parseOperand(lhs) || parser.parseComma() ||
      parser.parseOperand(rhs))
    return mlir::failure();

  if (parser.parseColonType(lhsType) || parser.parseComma() ||
      parser.parseType(rhsType))
    return mlir::failure();

  auto lhsQuantityType = llvm::dyn_cast<units::QuantityType>(lhsType);
  auto rhsQuantityType = llvm::dyn_cast<units::QuantityType>(rhsType);

  if (!lhsQuantityType || !rhsQuantityType)
    return parser.emitError(opLoc) << "operand types must be quantity types";

  auto inferredResultType =
      inferMulResultType(parser.getContext(), lhsQuantityType, rhsQuantityType);

  if (llvm::failed(inferredResultType))
    return parser.emitError(opLoc) << "failed to infer result type";

  result.addTypes(*inferredResultType);

  if (parser.resolveOperand(lhs, lhsType, result.operands) ||
      parser.resolveOperand(rhs, rhsType, result.operands))
    return mlir::failure();

  return mlir::success();
}

llvm::LogicalResult units::MulOp::verify() {
  auto lhsType = llvm::cast<units::QuantityType>(getLhs().getType());
  auto rhsType = llvm::cast<units::QuantityType>(getRhs().getType());
  auto resultType = llvm::cast<units::QuantityType>(getResult().getType());

  auto expectedType = inferMulResultType(getContext(), lhsType, rhsType);
  if (llvm::failed(expectedType))
    return emitOpError() << "failed to infer result unit";

  if (resultType != *expectedType)
    return emitOpError() << "expected result type `" << *expectedType << "`";

  return mlir::success();
}

void units::MulOp::print(mlir::OpAsmPrinter &printer) {
  printer << " " << getLhs() << ", " << getRhs() << " : ";
  printer.printType(getLhs().getType());
  printer << ", ";
  printer.printType(getRhs().getType());
}

//==================================================
// AddOp
//==================================================
static llvm::FailureOr<units::UnitAttr> addUnits(units::UnitAttr const &lhs,
                                                 units::UnitAttr const &rhs) {
  return applyBinaryUnitOp(lhs, rhs, units::algebra::add);
}

/**
 * Infer the result type of an add operation.
 */
static llvm::FailureOr<units::QuantityType>
inferAddResultType(mlir::MLIRContext *context, units::QuantityType lhsType,
                   units::QuantityType rhsType) {
  auto resultUnit = addUnits(lhsType.getUnit(), rhsType.getUnit());
  if (llvm::failed(resultUnit))
    return llvm::failure();

  return units::QuantityType::get(context, lhsType.getElementType(),
                                  *resultUnit);
}

void units::AddOp::build(mlir::OpBuilder &builder, mlir::OperationState &state,
                         mlir::Value lhs, mlir::Value rhs) {
  auto lhsType = llvm::cast<units::QuantityType>(lhs.getType());
  auto rhsType = llvm::cast<units::QuantityType>(rhs.getType());

  auto resultType = inferAddResultType(builder.getContext(), lhsType, rhsType);
  assert(llvm::succeeded(resultType) &&
         "failed to infer units.add result type");

  state.addOperands({lhs, rhs});
  state.addTypes(*resultType);
}

mlir::ParseResult units::AddOp::parse(mlir::OpAsmParser &parser,
                                      mlir::OperationState &result) {
  mlir::OpAsmParser::UnresolvedOperand lhs;
  mlir::OpAsmParser::UnresolvedOperand rhs;
  mlir::Type lhsType;
  mlir::Type rhsType;
  mlir::Type resultType;

  auto opLoc = parser.getCurrentLocation();
  if (parser.parseOperand(lhs) || parser.parseComma() ||
      parser.parseOperand(rhs))
    return mlir::failure();

  if (parser.parseColonType(lhsType) || parser.parseComma() ||
      parser.parseType(rhsType))
    return mlir::failure();

  auto lhsQuantityType = llvm::dyn_cast<units::QuantityType>(lhsType);
  auto rhsQuantityType = llvm::dyn_cast<units::QuantityType>(rhsType);
  if (!lhsQuantityType || !rhsQuantityType)
    return parser.emitError(opLoc) << "operand types must be quantity types";

  auto inferredResultType =
      inferAddResultType(parser.getContext(), lhsQuantityType, rhsQuantityType);
  if (llvm::failed(inferredResultType))
    return parser.emitError(opLoc) << "failed to infer result type";

  result.addTypes(*inferredResultType);

  if (parser.resolveOperand(lhs, lhsType, result.operands) ||
      parser.resolveOperand(rhs, rhsType, result.operands))
    return mlir::failure();

  return mlir::success();
}

llvm::LogicalResult units::AddOp::verify() {
  auto lhsType = llvm::cast<units::QuantityType>(getLhs().getType());
  auto rhsType = llvm::cast<units::QuantityType>(getRhs().getType());
  auto resultType = llvm::cast<units::QuantityType>(getResult().getType());

  auto expectedType = inferAddResultType(getContext(), lhsType, rhsType);
  if (llvm::failed(expectedType))
    return emitOpError() << "failed to infer result type";

  if (resultType != *expectedType)
    return emitOpError() << "expected result type `" << *expectedType << "`";

  return mlir::success();
}

void units::AddOp::print(mlir::OpAsmPrinter &printer) {
  printer << " " << getLhs() << ", " << getRhs() << " : ";
  printer.printType(getLhs().getType());
  printer << ", ";
  printer.printType(getRhs().getType());
}

//==================================================
// TableGen'd op method definitions
//==================================================
#define GET_OP_CLASSES
#include "Units/UnitsOps.cpp.inc"
