find_package(GTest REQUIRED)
include(GoogleTest)

add_executable(UnitsRsTests
  UnitsRsAbiTest.cpp
)

target_link_libraries(UnitsRsTests
  PRIVATE
  units_rs
  GTest::gtest_main
)

gtest_discover_tests(UnitsRsTests)
