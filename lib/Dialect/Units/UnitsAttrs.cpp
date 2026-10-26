#include "Units/UnitsAttrs.h"
#include "Units/UnitsAlgebra.h"

#include <llvm/Support/Error.h>
#include <llvm/Support/LogicalResult.h>
#include <mlir/IR/Diagnostics.h>
#include <mlir/IR/Location.h>
#include <mlir/IR/OpImplementation.h>
#include <mlir/Support/LLVM.h>

#include <llvm/ADT/STLExtras.h>
#include <llvm/ADT/SmallVector.h>
#include <llvm/ADT/TypeSwitch.h>

#define GET_ATTRDEF_CLASSES
#include "lib/Dialect/Units/UnitsAttrs.cpp.inc"

namespace mlir::units {

void UnitsDialect::registerAttributes() {
  addAttributes<
#define GET_ATTRDEF_LIST
#include "lib/Dialect/Units/UnitsAttrs.cpp.inc"
      >();
}

UnitAttr
UnitAttr::getChecked(::llvm::function_ref<InFlightDiagnostic()> emitError,
                     MLIRContext *context, ::llvm::StringRef expression) {
  auto expressionNormalized = algebra::canonicalize(expression);
  if (!expressionNormalized) {
    emitError() << "Failed to normalize unit expression: "
                << ::llvm::toString(expressionNormalized.takeError());
    return {};
  }

  return Base::getChecked(emitError, context, expressionNormalized.get());
}

UnitAttr UnitAttr::get(MLIRContext *context, ::llvm::StringRef expression) {
  return getChecked(
      [expression, context]() {
        return emitError(UnknownLoc::get(context))
               << "Critical error during unit construction: " << expression;
      },
      context, expression);
}

::llvm::LogicalResult
UnitAttr::verify(::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError,
                 ::llvm::StringRef expression) {

  auto expressionNormalized = algebra::canonicalize(expression);
  if (!expressionNormalized) {
    return emitError() << "Failed to normalize unit expression: "
                       << ::llvm::toString(expressionNormalized.takeError());
  }

  if (expression != expressionNormalized.get()) {
    return emitError() << "Expression must be in normalized form: "
                       << expression << " != " << expressionNormalized.get();
  }

  return mlir::success();
}

Attribute UnitAttr::parse(AsmParser &parser, Type type) {
  if (parser.parseLess())
    return {};

  std::string expression;
  if (parser.parseString(&expression) || parser.parseGreater())
    return {};

  return UnitAttr::get(parser.getContext(), expression);
}

void UnitAttr::print(AsmPrinter &printer) const {
  printer << "<";
  printer.printString(getExpression());
  printer << ">";
}

} // namespace mlir::units
