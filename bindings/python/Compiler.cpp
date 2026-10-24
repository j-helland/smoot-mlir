#include <cstddef>
#include <memory>

#include <llvm/ADT/StringExtras.h>

#include <mlir/Conversion/ArithToLLVM/ArithToLLVM.h>
#include <mlir/Conversion/ControlFlowToLLVM/ControlFlowToLLVM.h>
#include <mlir/Conversion/FuncToLLVM/ConvertFuncToLLVMPass.h>
#include <mlir/Conversion/ReconcileUnrealizedCasts/ReconcileUnrealizedCasts.h>
#include <mlir/Conversion/SCFToControlFlow/SCFToControlFlow.h>
#include <mlir/Dialect/Arith/IR/Arith.h>
#include <mlir/Dialect/Func/IR/FuncOps.h>
#include <mlir/Dialect/LLVMIR/LLVMDialect.h>
#include <mlir/ExecutionEngine/ExecutionEngine.h>
#include <mlir/IR/BuiltinAttributes.h>
#include <mlir/IR/BuiltinOps.h>
#include <mlir/IR/DialectRegistry.h>
#include <mlir/IR/MLIRContext.h>
#include <mlir/IR/OwningOpRef.h>
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

static void configureContext(mlir::ModuleOp module) {
  mlir::DialectRegistry registry;
  registry.insert<mlir::func::FuncDialect, mlir::arith::ArithDialect,
                  mlir::LLVM::LLVMDialect, mlir::units::UnitsDialect>();

  module->getContext()->appendDialectRegistry(registry);
}

static void lowerUnitsToArith(mlir::ModuleOp module) {
  mlir::PassManager unitsPasses(module->getContext());
  unitsPasses.addPass(mlir::units::createUnitsToStandard());
  if (mlir::failed(unitsPasses.run(module.getOperation()))) {
    throw BackendError("failed to lower Units operations");
  }
}

static std::size_t prepareEntrypoint(mlir::ModuleOp module,
                                     const std::string &entrypoint) {
  auto entry = module.lookupSymbol<mlir::func::FuncOp>(entrypoint);
  if (!entry || entry.isExternal()) {
    throw BackendError("entrypoint must name a function definition");
  }

  auto type = entry.getFunctionType();
  if (type.getNumResults() != 1 || !type.getResult(0).isF64()) {
    throw BackendError("entrypoint must return exactly one f64");
  }
  for (auto inputType : type.getInputs()) {
    if (!inputType.isF64()) {
      throw BackendError("entrypoint arguments must all be f64");
    }
  }

  entry->setAttr(mlir::LLVM::LLVMDialect::getEmitCWrapperAttrName(),
                 mlir::UnitAttr::get(module->getContext()));

  return type.getNumInputs();
}

static void lowerToLLVM(mlir::ModuleOp module) {
  mlir::PassManager llvmPasses(module->getContext());

  llvmPasses.addPass(mlir::createSCFToControlFlowPass());
  llvmPasses.addPass(mlir::createArithToLLVMConversionPass());
  llvmPasses.addPass(mlir::createConvertControlFlowToLLVMPass());
  llvmPasses.addPass(mlir::createConvertFuncToLLVMPass());
  llvmPasses.addPass(mlir::createReconcileUnrealizedCastsPass());

  if (mlir::failed(llvmPasses.run(module.getOperation()))) {
    throw BackendError("failed to lower module to LLVM");
  }
}

// NOTE(jwh): Lowering passes may mutate the caller's IR.
//            Clone into an OwningOpRef if this becomes a concern.
std::unique_ptr<CompiledFunction> compileMlir(mlir::ModuleOp module,
                                              const std::string &entrypoint) {
  configureContext(module);

  if (mlir::failed(mlir::verify(module.getOperation()))) {
    throw BackendError("failed to verify MLIR module");
  }

  // Lowering passes.
  lowerUnitsToArith(module);
  auto numArgs = prepareEntrypoint(module, entrypoint);
  lowerToLLVM(module);

  auto engine = mlir::ExecutionEngine::create(module.getOperation());
  if (!engine) {
    throw BackendError(llvm::toString(engine.takeError()));
  }

  return std::make_unique<CompiledFunction>(std::move(*engine), entrypoint,
                                            numArgs);
}

} // namespace units::backend
