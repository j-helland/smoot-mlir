#include "Units/UnitsOps.h"
#include "llvm/Support/Casting.h"

// For `let hasCustomAssemblyFormat = 1`
mlir::ParseResult units::ConstOp::parse(mlir::OpAsmParser &parser,
                                        mlir::OperationState &result) {
  double value;
  std::string unit;
  mlir::Type type;

  if (parser.parseFloat(value))
    return mlir::failure();

  if (parser.parseString(&unit))
    return mlir::failure();

  auto typeLoc = parser.getCurrentLocation();
  if (parser.parseColonType(type))
    return mlir::failure();

  const auto floatType = llvm::dyn_cast<mlir::FloatType>(type);
  if (!floatType)
    return parser.emitError(typeLoc) << "expected floating-point result type";

  result.addAttribute("value", mlir::FloatAttr::get(floatType, value));
  result.addAttribute("unit", mlir::StringAttr::get(parser.getContext(), unit));
  result.addTypes(type);
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
  printer << " ";
  printer.printAttribute(getUnitAttr());
  printer << " : ";
  printer.printType(getResult().getType());
}

// For `let hasVerifier = 1`
llvm::LogicalResult units::ConstOp::verify() {
  llvm::StringRef unit = getUnit();
  if (unit.empty())
    return emitOpError() << "unit must not be empty";

  auto resultType = llvm::dyn_cast<mlir::FloatType>(getResult().getType());
  if (!resultType)
    return emitOpError() << "result must be a floating-point type";

  if (getValueAttr().getType() != getResult().getType())
    return emitOpError() << "value attribute type must match result type";

  return mlir::success();
}

//==================================================
// TableGen'd op method definitions
//==================================================
#define GET_OP_CLASSES
#include "Units/UnitsOps.cpp.inc"
