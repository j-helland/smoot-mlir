set(LLVM_TARGET_DEFINITIONS UnitsDialect.td)
mlir_tablegen(UnitsDialect.h.inc -gen-dialect-decls -dialect=units)
mlir_tablegen(UnitsDialect.cpp.inc -gen-dialect-defs -dialect=units)
add_public_tablegen_target(MLIRUnitsDialectIncGen)

set(LLVM_TARGET_DEFINITIONS UnitsOps.td)
mlir_tablegen(UnitsOps.h.inc -gen-op-decls)
mlir_tablegen(UnitsOps.cpp.inc -gen-op-defs)
add_public_tablegen_target(MLIRUnitsOpsIncGen)

set(LLVM_TARGET_DEFINITIONS UnitsTypes.td)
mlir_tablegen(UnitsTypes.h.inc -gen-typedef-decls)
mlir_tablegen(UnitsTypes.cpp.inc -gen-typedef-defs)
add_public_tablegen_target(MLIRUnitsTypesIncGen)

add_mlir_dialect_library(MLIRUnits
  UnitsDialect.cpp
  UnitsOps.cpp
  UnitsTypes.cpp

  ADDITIONAL_HEADER_DIRS
  ${PROJECT_SOURCE_DIR}/lib/Dialect/Units

  DEPENDS
  MLIRUnitsDialectIncGen
  MLIRUnitsOpsIncGen
  MLIRUnitsTypesIncGen

  LINK_LIBS PUBLIC
  MLIRIR
  MLIRSupport
)
