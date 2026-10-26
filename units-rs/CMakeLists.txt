find_program(CARGO_EXE cargo REQUIRED)
find_program(RUSTC_EXE rustc REQUIRED)
find_program(CBINDGEN_EXE cbindgen REQUIRED)

set(UNITS_RS_DIR ${CMAKE_CURRENT_SOURCE_DIR})

#==================================================
# Generate C ABI header
#==================================================
set(UNITS_RS_INCLUDE_DIR ${UNITS_RS_DIR}/include)
set(UNITS_RS_HEADER ${UNITS_RS_INCLUDE_DIR}/units_rs.h)
set(UNITS_RS_DEPFILE "${CMAKE_CURRENT_BINARY_DIR}/units_rs.d")

file(MAKE_DIRECTORY "${UNITS_RS_INCLUDE_DIR}")

add_custom_command(
  OUTPUT "${UNITS_RS_HEADER}"

  COMMAND "${CMAKE_COMMAND}" -E make_directory
          "${UNITS_RS_INCLUDE_DIR}"

  COMMAND "${CBINDGEN_EXE}"
          --config "${UNITS_RS_DIR}/cbindgen.toml"
          --crate units-rs
          --output "${UNITS_RS_HEADER}"
          --depfile "${UNITS_RS_DEPFILE}"

  # cbindgen may leave the timestamp unchanged if the contents match
  COMMAND "${CMAKE_COMMAND}" -E touch "${UNITS_RS_HEADER}"

  DEPENDS
      "${UNITS_RS_DIR}/Cargo.toml"
      "${UNITS_RS_DIR}/Cargo.lock"
      "${UNITS_RS_DIR}/cbindgen.toml"
      "${CBINDGEN_EXE}"

  DEPFILE "${UNITS_RS_DEPFILE}"

  WORKING_DIRECTORY "${UNITS_RS_DIR}"
  COMMENT "Generating units_rs.h"
  VERBATIM
)

add_custom_target(units_rs_header
  DEPENDS "${UNITS_RS_HEADER}"
)

#==================================================
# Build C ABI
#==================================================
set(UNITS_RS_TARGET_DIR ${CMAKE_CURRENT_BINARY_DIR}/cargo-target)
set(UNITS_RS_LIB ${UNITS_RS_TARGET_DIR}/release/libunits_rs.a)

add_custom_target(units_rs_static
  COMMAND ${CMAKE_COMMAND} -E env
          MACOSX_DEPLOYMENT_TARGET=${CMAKE_OSX_DEPLOYMENT_TARGET}
          ${CARGO_EXE} build
          --release
          --manifest-path ${UNITS_RS_DIR}/Cargo.toml
          --target-dir ${UNITS_RS_TARGET_DIR}
  BYPRODUCTS ${UNITS_RS_LIB}
  WORKING_DIRECTORY ${UNITS_RS_DIR}
  VERBATIM
)

add_library(units_rs STATIC IMPORTED GLOBAL)

set_target_properties(units_rs PROPERTIES
  IMPORTED_LOCATION ${UNITS_RS_LIB}
  INTERFACE_INCLUDE_DIRECTORIES ${UNITS_RS_DIR}/include
)

add_dependencies(units_rs units_rs_header units_rs_static)
