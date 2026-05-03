add_subdirectory(Dialect)

add_custom_target(check-units-cpp
  COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
  DEPENDS UnitsDialectTests
  USES_TERMINAL
)
