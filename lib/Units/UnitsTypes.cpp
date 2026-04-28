#include "Units/UnitsTypes.h"

mlir::Type units::QuantityType::parse(mlir::AsmParser &parser) {
  mlir::Type elementType;
  std::string unit;

  if (parser.parseLess() || parser.parseType(elementType) ||
      parser.parseComma() || parser.parseString(&unit) || parser.parseGreater())
    return {};

  return QuantityType::get(parser.getContext(), elementType, unit);
}

void units::QuantityType::print(mlir::AsmPrinter &printer) const {
  printer << "<";
  printer.printType(getElementType());
  printer << ", ";
  printer.printString(getUnit());
  printer << ">";
}

#define GET_TYPEDEF_CLASSES
#include "Units/UnitsTypes.cpp.inc"

void units::UnitsDialect::registerTypes() {
  addTypes<
#define GET_TYPEDEF_LIST
#include "Units/UnitsTypes.cpp.inc"
      >();
}
