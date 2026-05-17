add_subdirectory(Dialect)
add_subdirectory(UnitsRs)

add_custom_target(check-units-cpp
  COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
  DEPENDS UnitsDialectTests UnitsRsTests
  USES_TERMINAL
)
