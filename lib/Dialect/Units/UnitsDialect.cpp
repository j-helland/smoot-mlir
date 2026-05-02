#include "lib/Dialect/Units/UnitsDialect.h"

#include "lib/Dialect/Units/UnitsOps.h"
#include "lib/Dialect/Units/UnitsTypes.h"

#include "mlir/IR/Builders.h"
#include "llvm/ADT/TypeSwitch.h"

#include "lib/Dialect/Units/UnitsDialect.cpp.inc"
#define GET_TYPEDEF_CLASSES
#include "lib/Dialect/Units/UnitsTypes.cpp.inc"

namespace mlir {
namespace units {

void UnitsDialect::initialize() {
  addTypes<
#define GET_TYPEDEF_LIST
#include "lib/Dialect/Units/UnitsTypes.cpp.inc"
      >();

  addOperations<
#define GET_OP_LIST
#include "lib/Dialect/Units/UnitsOps.cpp.inc"
      >();
}

} // namespace units
} // namespace mlir
