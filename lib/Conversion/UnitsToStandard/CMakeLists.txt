set(LLVM_TARGET_DEFINITIONS UnitsToStandard.td)
mlir_tablegen(UnitsToStandard.h.inc -gen-pass-decls -name UnitsToStandard)
add_public_tablegen_target(UnitsToStandardPassIncGen)

add_mlir_library(UnitsToStandard
  UnitsToStandard.cpp

  ADDITIONAL_HEADER_DIRS
  ${PROJECT_SOURCE_DIR}/lib/Conversion/UnitsToStandard

  DEPENDS
  UnitsToStandardPassIncGen
  MLIRUnitsOpsIncGen

  LINK_COMPONENTS
  Core

  LINK_LIBS PUBLIC
  MLIRUnits
)

mlir_target_link_libraries(UnitsToStandard PUBLIC
  MLIRArithDialect
  MLIRFuncDialect
  MLIRFuncTransforms
  MLIRSCFDialect
  MLIRTransforms
)
