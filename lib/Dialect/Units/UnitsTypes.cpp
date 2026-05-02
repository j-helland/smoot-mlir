#include "Units/UnitsTypes.h"

namespace units = mlir::units;

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
