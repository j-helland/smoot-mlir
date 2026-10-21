find_package(Python 3.12 REQUIRED COMPONENTS
  Interpreter
  Development.Module
)
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(_units_backend
  UnitsBackendModule.cpp
  CompiledFunction.cpp
  Compiler.cpp
)

target_link_libraries(_units_backend PRIVATE
  UnitsCAPI
  MLIRUnits
  UnitsToStandard

  MLIRCAPIIR
  MLIRIR
  MLIRParser
  MLIRPass
  MLIRExecutionEngine
  MLIRArithToLLVM
  MLIRFuncToLLVM
  MLIRReconcileUnrealizedCasts
  MLIRBuiltinToLLVMIRTranslation
  MLIRLLVMToLLVMIRTranslation
)

# Sanitizer builds must not replace the extension imported by the regular
# Python environment: ASan cannot initialize when loaded through Python's dlopen.
set(UNITS_PYTHON_LIBRARY_DIR "${PROJECT_SOURCE_DIR}/frontend/python/src/units")
if(UNITS_SANITIZERS)
  set(UNITS_PYTHON_LIBRARY_DIR "${CMAKE_CURRENT_BINARY_DIR}")
endif()

set_target_properties(_units_backend PROPERTIES
  CXX_VISIBILITY_PRESET default
  VISIBILITY_INLINES_HIDDEN OFF
  LIBRARY_OUTPUT_DIRECTORY
    "${UNITS_PYTHON_LIBRARY_DIR}"
)

# tablegen
set(LLVM_TARGET_DEFINITIONS
  "${CMAKE_CURRENT_SOURCE_DIR}/UnitsOps.td"
)

mlir_tablegen(_units_ops_gen.py
  -gen-python-op-bindings
  -bind-dialect=units
)

add_public_tablegen_target(UnitsPythonOpsGen)

set(UNITS_PYTHON_DIALECT_DIR
  "${PROJECT_SOURCE_DIR}/frontend/python/src/units/dialects"
)

add_custom_target(UnitsPythonBindings ALL
  COMMAND "${CMAKE_COMMAND}" -E make_directory
    "${UNITS_PYTHON_DIALECT_DIR}"
  COMMAND "${CMAKE_COMMAND}" -E copy_if_different
    "${CMAKE_CURRENT_BINARY_DIR}/_units_ops_gen.py"
    "${UNITS_PYTHON_DIALECT_DIR}/_units_ops_gen.py"
  BYPRODUCTS
    "${UNITS_PYTHON_DIALECT_DIR}/_units_ops_gen.py"
  VERBATIM
)

add_dependencies(UnitsPythonBindings UnitsPythonOpsGen)
add_dependencies(_units_backend UnitsPythonBindings)
