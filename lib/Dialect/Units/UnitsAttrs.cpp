#include "Units/UnitsAttrs.h"

#include <mlir/IR/OpImplementation.h>
#include <mlir/Support/LLVM.h>

#include <llvm/ADT/STLExtras.h>
#include <llvm/ADT/SmallVector.h>

#include <cstdint>

namespace units = mlir::units;

mlir::Attribute units::UnitAttr::parse(mlir::AsmParser &parser,
                                       mlir::Type type) {
  if (parser.parseLess())
    return {};

  std::string expression;
  if (parser.parseString(&expression) || parser.parseGreater())
    return {};

  return units::UnitAttr::get(parser.getContext(), expression);
}

void units::UnitAttr::print(mlir::AsmPrinter &printer) const {
  printer << "<";
  printer.printString(getExpression());
  printer << ">";
}
