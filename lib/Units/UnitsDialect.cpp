#include "Units/UnitsDialect.h"
#include "Units/UnitsOps.h"

#include "mlir/IR/DialectImplementation.h"

#include "Units/UnitsDialect.cpp.inc"

void units::UnitsDialect::initialize() {
  addOperations<
#define GET_OP_LIST
#include "Units/UnitsOps.cpp.inc"
      >();
}
