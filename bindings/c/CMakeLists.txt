add_mlir_public_c_api_library(UnitsCAPI
  UnitsDialect.cpp

  LINK_LIBS PUBLIC
  MLIRUnits
)
