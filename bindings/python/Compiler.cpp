#include <memory>

#include <llvm/ADT/StringExtras.h>

#include <mlir/Conversion/ArithToLLVM/ArithToLLVM.h>
#include <mlir/Conversion/FuncToLLVM/ConvertFuncToLLVMPass.h>
#include <mlir/Conversion/ReconcileUnrealizedCasts/ReconcileUnrealizedCasts.h>
#include <mlir/Dialect/Arith/IR/Arith.h>
#include <mlir/Dialect/Func/IR/FuncOps.h>
#include <mlir/Dialect/LLVMIR/LLVMDialect.h>
#include <mlir/ExecutionEngine/ExecutionEngine.h>
#include <mlir/IR/BuiltinAttributes.h>
#include <mlir/IR/BuiltinOps.h>
#include <mlir/IR/DialectRegistry.h>
#include <mlir/IR/MLIRContext.h>
#include <mlir/IR/Verifier.h>
#include <mlir/Parser/Parser.h>
#include <mlir/Pass/Pass.h>
#include <mlir/Pass/PassManager.h>
#include <mlir/Support/LLVM.h>
#include <mlir/Target/LLVMIR/Dialect/Builtin/BuiltinToLLVMIRTranslation.h>
#include <mlir/Target/LLVMIR/Dialect/LLVMIR/LLVMToLLVMIRTranslation.h>

#include "Units/UnitsDialect.h"
#include "lib/Conversion/UnitsToStandard/UnitsToStandard.h"
#include "BackendError.h"
#include "CompiledFunction.h"
#include "Compiler.h"

namespace units::backend {

std::unique_ptr<CompiledFunction> compileMlir(const std::string &text,
                                              const std::string &entryPoint) {
  mlir::DialectRegistry registry;
  registry.insert<mlir::func::FuncDialect, mlir::arith::ArithDialect,
                  mlir::LLVM::LLVMDialect, mlir::units::UnitsDialect>();
  mlir::MLIRContext context(registry);
  auto module = mlir::parseSourceString<mlir::ModuleOp>(text, &context);

  if (!module) {
    throw BackendError("failed to parse placeholder module");
  }
  if (mlir::failed(mlir::verify(module.get()))) {
    throw BackendError("failed to verify placeholder module");
  }

  // lowering
  mlir::PassManager unitsPasses(&context);
  unitsPasses.addPass(mlir::units::createUnitsToStandard());
  if (mlir::failed(unitsPasses.run(module.get()))) {
    throw BackendError("failed to lower Units operations");
  }

  auto entry = module->lookupSymbol<mlir::func::FuncOp>(entryPoint);
  if (!entry || entry.isExternal()) {
    throw BackendError("entrypoint must name a function definition");
  }

  auto type = entry.getFunctionType();
  if (type.getNumInputs() != 1 || type.getNumResults() != 1 ||
      !type.getInput(0).isF64() || !type.getResult(0).isF64()) {
    throw BackendError("entrypoint must have function signature (f64) -> f64");
  }

  entry->setAttr("llvm.emit_c_interface", mlir::UnitAttr::get(&context));
  mlir::PassManager llvmPasses(&context);
  llvmPasses.addPass(mlir::createArithToLLVMConversionPass());
  llvmPasses.addPass(mlir::createConvertFuncToLLVMPass());
  llvmPasses.addPass(mlir::createReconcileUnrealizedCastsPass());
  if (mlir::failed(llvmPasses.run(module.get()))) {
    throw BackendError("failed to lower module to LLVM");
  }

  mlir::registerBuiltinDialectTranslation(context);
  mlir::registerLLVMDialectTranslation(context);

  auto maybeEngine = mlir::ExecutionEngine::create(module->getOperation());
  if (!maybeEngine) {
    throw BackendError(llvm::toString(maybeEngine.takeError()));
  }
  return std::make_unique<CompiledFunction>(std::move(*maybeEngine),
                                            entryPoint);
}

} // namespace units::backend
