#include "Units/UnitsAttrs.h"
#include "mlir/IR/OpImplementation.h"
#include "mlir/Support/LLVM.h"
#include "llvm/ADT/STLExtras.h"
#include "llvm/ADT/SmallVector.h"
#include <cstdint>

namespace units = mlir::units;

mlir::Attribute units::UnitAttr::parse(mlir::AsmParser &parser,
                                       mlir::Type type) {
  if (parser.parseLess())
    return {};

  if (parser.parseKeyword("dims") || parser.parseEqual() ||
      parser.parseLSquare())
    return {};

  llvm::SmallVector<int64_t> dims;
  if (mlir::succeeded(parser.parseOptionalRSquare())) {
    if (parser.parseGreater())
      return {};
    return units::UnitAttr::get(parser.getContext(), dims);
  }

  if (parser.parseCommaSeparatedList([&]() {
        int64_t dim = 0;
        if (parser.parseInteger(dim))
          return mlir::failure();
        dims.push_back(dim);
        return mlir::success();
      }))
    return {};

  if (parser.parseRSquare() || parser.parseGreater()) return {};

  while (!dims.empty() && dims.back() == 0) dims.pop_back();

  return units::UnitAttr::get(parser.getContext(), dims);
}

void units::UnitAttr::print(mlir::AsmPrinter &printer) const {
    printer << "<dims = [";
    llvm::interleaveComma(getDims(), printer, [&](int64_t dim) {
        printer << dim;
    });
    printer << "]>";
}
