set(LIBS
  UnitsToStandard
  MLIRMlirOptMain
  MLIRRegisterAllDialects
  MLIRRegisterAllPasses
  MLIRTransforms
)

add_llvm_executable(units-opt units-opt.cpp)

llvm_update_compile_flags(units-opt)
target_link_libraries(units-opt PRIVATE ${LIBS})

mlir_check_all_link_libraries(units-opt)
