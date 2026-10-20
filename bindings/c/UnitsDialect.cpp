#include "bindings/c/UnitsDialect.h"
#include "Units/UnitsAttrs.h"
#include "Units/UnitsDialect.h"
#include "Units/UnitsTypes.h"

#include <mlir/CAPI/IR.h>
#include <mlir/CAPI/Registration.h>
#include <mlir/IR/Types.h>

MLIR_DEFINE_CAPI_DIALECT_REGISTRATION(Units, units, mlir::units::UnitsDialect)

MlirType mlirUnitsQuantityTypeGet(MlirType elementType,
                                  MlirStringRef unitExpression) {
  mlir::Type element = unwrap(elementType);
  auto *context = element.getContext();
  auto unit = mlir::units::UnitAttr::get(context, unwrap(unitExpression));
  return wrap(mlir::units::QuantityType::get(context, element, unit));
}
