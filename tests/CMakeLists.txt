# LLVM_TOOLS_DIR points at LLVM's bin dir, which contains FileCheck/count/not,
# while MLIR tools live in the MLIR package's bin dir. Pass both through to lit
# so tests can resolve %units-opt, %mlir-opt, and %FileCheck explicitly.
find_program(MLIR_OPT_EXECUTABLE NAMES mlir-opt REQUIRED)
get_filename_component(MLIR_TOOLS_DIR "${MLIR_OPT_EXECUTABLE}" DIRECTORY)

configure_lit_site_cfg(
    ${CMAKE_CURRENT_SOURCE_DIR}/lit.cmake.site.cfg.py.in
    ${CMAKE_CURRENT_BINARY_DIR}/lit.site.cfg.py
    MAIN_CONFIG
    ${CMAKE_CURRENT_SOURCE_DIR}/lit.cmake.cfg.py
)

set(MLIR_UNITS_TEST_DEPENDS
    FileCheck count not
    mlir-opt
    mlir-runner
    units-opt
)

find_program(LIT_EXECUTABLE NAMES llvm-lit llvm-lit.py lit REQUIRED)
message(STATUS "Using lit executable: ${LIT_EXECUTABLE}")

set(LIT_ARGS "${LLVM_LIT_ARGS}")
separate_arguments(LIT_ARGS)

add_custom_target(check-mlir-units
  COMMAND ${LIT_EXECUTABLE} ${LIT_ARGS} ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Running the MLIR units regression tests"
  USES_TERMINAL
)
add_dependencies(check-mlir-units ${MLIR_UNITS_TEST_DEPENDS})
