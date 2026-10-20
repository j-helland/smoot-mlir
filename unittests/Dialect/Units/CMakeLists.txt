find_package(GTest REQUIRED)
include(GoogleTest)

add_executable(UnitsDialectTests
  UnitAttrTest.cpp
  QuantityTypeTest.cpp
)

target_link_libraries(UnitsDialectTests
  PRIVATE
  MLIRUnits
  GTest::gtest_main
)

mlir_target_link_libraries(UnitsDialectTests
  PRIVATE
  MLIRIR
  MLIRSupport
)

gtest_add_tests(TARGET UnitsDialectTests)
