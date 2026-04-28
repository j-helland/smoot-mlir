#include "Units/UnitsDialect.h"
#include "Units/UnitsOps.h"
#include "Units/UnitsTypes.h"

#include "Units/UnitsDialect.cpp.inc"

void units::UnitsDialect::initialize() {
  registerTypes();

  addOperations<
#define GET_OP_LIST
#include "Units/UnitsOps.cpp.inc"
      >();
}
