cmake_minimum_required(VERSION 3.26.0)

# Cargo and CMake do not automatically coordinate on the macOS deploy target
# so we need to wire that ourselves.
if(APPLE AND NOT DEFINED CMAKE_OSX_DEPLOYMENT_TARGET)
  set(CMAKE_OSX_DEPLOYMENT_TARGET "14.0" CACHE STRING "Minimum macOS deployment version")
endif()

project(mlir-units LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ standard to conform to")
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(BUILD_DEPS ON)

option(UNITS_ENABLE_CLANG_TIDY "Run clang-tidy during C++ builds" OFF)
option(UNITS_ENABLE_ASAN "Build with AddressSanitizer" OFF)
option(UNITS_ENABLE_UBSAN "Build with UndefinedBehaviorSanitizer" OFF)

set(UNITS_SANITIZERS)
if(UNITS_ENABLE_ASAN)
  list(APPEND UNITS_SANITIZERS address)
endif()
if(UNITS_ENABLE_UBSAN)
  list(APPEND UNITS_SANITIZERS undefined)
endif()

if(UNITS_SANITIZERS)
  list(JOIN UNITS_SANITIZERS "," UNITS_SANITIZER_LIST)
  add_compile_options(-fsanitize=${UNITS_SANITIZER_LIST}
                      -fno-omit-frame-pointer)
  add_link_options(-fsanitize=${UNITS_SANITIZER_LIST})
  message(STATUS "Enabled sanitizers: ${UNITS_SANITIZER_LIST}")
endif()

if(UNITS_ENABLE_CLANG_TIDY)
  find_program(CLANG_TIDY_EXE NAMES clang-tidy REQUIRED)
  set(CMAKE_CXX_CLANG_TIDY "${CLANG_TIDY_EXE}")
endif()

find_package(MLIR REQUIRED CONFIG)
message(STATUS "Using MLIRConfig.cmake in: ${MLIR_DIR}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

if(NOT MLIR_TABLEGEN_EXE_ABSOLUTE)
  message(FATAL_ERROR
    "Set MLIR_TABLEGEN_EXE_ABSOLUTE to the matching mlir-tblgen"
  )
endif()
message(STATUS "Using mlir-tblgen ${MLIR_TABLEGEN_EXE_ABSOLUTE}")
set(MLIR_TABLEGEN_EXE "${MLIR_TABLEGEN_EXE_ABSOLUTE}")
set(MLIR_TABLEGEN_TARGET "${MLIR_TABLEGEN_EXE}")
set(MLIR_LINK_MLIR_DYLIB ON)
message(STATUS "Using MLIR TableGen executable: ${MLIR_TABLEGEN_EXE}")

set(MLIR_BINARY_DIR ${CMAKE_BINARY_DIR})

include(AddLLVM)
include(TableGen)
include(CTest)

list(APPEND CMAKE_MODULE_PATH "${MLIR_CMAKE_DIR}")
include(AddMLIR)
include_directories(${LLVM_INCLUDE_DIRS})
include_directories(${MLIR_INCLUDE_DIRS})
include_directories(${PROJECT_SOURCE_DIR})
include_directories(${PROJECT_SOURCE_DIR}/externals/llvm-project)
include_directories(${PROJECT_SOURCE_DIR}/lib/Dialect)
include_directories(${PROJECT_BINARY_DIR})
include_directories(${PROJECT_BINARY_DIR}/lib/Dialect)

# core
add_subdirectory(units-rs)
add_subdirectory(lib)
add_subdirectory(tools)
add_subdirectory(bindings/python)

# tests
add_subdirectory(mlir-tests)
add_subdirectory(unittests)

add_custom_target(check-units
  DEPENDS check-units-mlir check-units-cpp
)
