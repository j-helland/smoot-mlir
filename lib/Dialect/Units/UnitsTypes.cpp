#include "Units/UnitsAttrs.h"
#include "Units/UnitsTypes.h"
#include "mlir/IR/OpImplementation.h"

namespace units = mlir::units;

mlir::Type units::QuantityType::parse(mlir::AsmParser &parser) {
  mlir::Type elementType;
  units::UnitAttr unit;

  if (parser.parseLess() || parser.parseType(elementType) ||
      parser.parseComma() || parser.parseAttribute(unit) ||
      parser.parseGreater())
    return {};

  return units::QuantityType::get(parser.getContext(), elementType, unit);
}

void units::QuantityType::print(mlir::AsmPrinter &printer) const {
  printer << "<";
  printer.printType(getElementType());
  printer << ", ";
  printer.printAttribute(getUnit());
  printer << ">";
}
