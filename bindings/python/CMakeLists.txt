find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_units_backend
  UnitsBackendModule.cpp
  CompiledFunction.cpp
  Compiler.cpp
)

target_link_libraries(_units_backend PRIVATE
  MLIRUnits
  UnitsToStandard
  MLIR
  MLIRExecutionEngine
)

set_target_properties(_units_backend PROPERTIES
  CXX_VISIBILITY_PRESET default
  VISIBILITY_INLINES_HIDDEN OFF
  LIBRARY_OUTPUT_DIRECTORY
    ${PROJECT_SOURCE_DIR}/frontend/python/src/units
)
