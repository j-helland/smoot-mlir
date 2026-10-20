#pragma once

#include <mlir-c/IR.h>
#include <mlir-c/Support.h>

#ifdef __cplusplus
extern "C" {
#endif

MLIR_DECLARE_CAPI_DIALECT_REGISTRATION(Units, units);

MLIR_CAPI_EXPORTED MlirType
mlirUnitsQuantityTypeGet(MlirType elementType, MlirStringRef unitExpression);

#ifdef __cplusplus
}
#endif
