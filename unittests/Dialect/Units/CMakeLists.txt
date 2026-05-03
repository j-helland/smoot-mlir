find_package(GTest REQUIRED)
include(GoogleTest)

add_executable(UnitsDialectTests
  UnitAttrTest.cpp
  QuantityTypeTest.cpp
)

target_link_libraries(UnitsDialectTests
  PRIVATE
  MLIRUnits
  MLIRIR
  MLIRSupport
  GTest::gtest
  GTest::gtest_main
)

gtest_discover_tests(UnitsDialectTests)
