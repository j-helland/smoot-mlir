#include "bindings/c/UnitsDialect.h"
#include "Units/UnitsDialect.h"

#include <mlir/CAPI/Registration.h>

MLIR_DEFINE_CAPI_DIALECT_REGISTRATION(Units, units, mlir::units::UnitsDialect)
