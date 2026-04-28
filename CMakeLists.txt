cmake_minimum_required(VERSION 3.20)

project(units-mlir-demo LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

find_package(MLIR REQUIRED CONFIG)

message(STATUS "Using MLIRConfig.cmake in: ${MLIR_DIR}")

list(APPEND CMAKE_MODULE_PATH "${MLIR_CMAKE_DIR}")
list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")

include(AddLLVM)
include(AddMLIR)

if(NOT IS_ABSOLUTE "${MLIR_TABLEGEN_EXE}")
  find_program(MLIR_TABLEGEN_EXE_PATH "${MLIR_TABLEGEN_EXE}" REQUIRED)
  set(MLIR_TABLEGEN_EXE "${MLIR_TABLEGEN_EXE_PATH}")
endif()
set(MLIR_TABLEGEN_TARGET "${MLIR_TABLEGEN_EXE}")

message(STATUS "Using MLIR tablegen: ${MLIR_TABLEGEN_EXE}")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/include)
include_directories(${LLVM_INCLUDE_DIRS})
include_directories(${MLIR_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

add_subdirectory(include/Units)

add_llvm_library(UnitsDialectPlugin
  MODULE
  lib/Units/UnitsDialect.cpp
  lib/Units/UnitsTypes.cpp
  lib/Units/UnitsOps.cpp
  lib/Units/UnitsDialectPlugin.cpp

  DEPENDS
  MLIRUnitsDialectIncGen
  MLIRUnitsOpsIncGen
  MLIRUnitsTypesIncGen

  PLUGIN_TOOL
  mlir-opt

  LINK_LIBS
  MLIR
)

#==================================================
# Testing
#==================================================
find_program(LIT_EXECUTABLE lit REQUIRED)
find_program(MLIR_OPT_EXECUTABLE mlir-opt REQUIRED)
find_program(FILECHECK_EXECUTABLE FileCheck REQUIRED)

set(UNITS_DIALECT_PLUGIN "${CMAKE_CURRENT_BINARY_DIR}/UnitsDialectPlugin${CMAKE_SHARED_LIBRARY_SUFFIX}")

configure_file(
  test/lit.site.cfg.py.in
  ${CMAKE_CURRENT_BINARY_DIR}/test/lit.site.cfg.py
  @ONLY
)

add_custom_target(CheckUnits
  COMMAND ${LIT_EXECUTABLE} -sv ${CMAKE_CURRENT_BINARY_DIR}/test
  DEPENDS UnitsDialectPlugin
)
