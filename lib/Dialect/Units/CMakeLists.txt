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

set(LLVM_TARGET_DEFINITIONS UnitsAttrs.td)
mlir_tablegen(UnitsAttrs.h.inc -gen-attrdef-decls)
mlir_tablegen(UnitsAttrs.cpp.inc -gen-attrdef-defs)
add_public_tablegen_target(MLIRUnitsAttrsIncGen)

add_mlir_dialect_library(MLIRUnits
  UnitsDialect.cpp
  UnitsOps.cpp
  UnitsTypes.cpp
  UnitsAttrs.cpp
  UnitsAlgebra.cpp

  ADDITIONAL_HEADER_DIRS
  ${PROJECT_SOURCE_DIR}/lib/Dialect/Units

  DEPENDS
  MLIRUnitsDialectIncGen
  MLIRUnitsOpsIncGen
  MLIRUnitsTypesIncGen
  MLIRUnitsAttrsIncGen

  LINK_LIBS PUBLIC
  units_rs
)

mlir_target_link_libraries(MLIRUnits PUBLIC
  MLIRIR
  MLIRSupport
)
