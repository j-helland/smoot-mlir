find_program(CARGO_EXE cargo REQUIRED)
find_program(RUSTC_EXE rustc REQUIRED)

set(UNITS_RS_DIR ${CMAKE_CURRENT_SOURCE_DIR})
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

add_dependencies(units_rs units_rs_static)
