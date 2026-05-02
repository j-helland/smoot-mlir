#include "lib/Conversion/UnitsToStandard/UnitsToStandard.h"
#include "lib/Dialect/Units/UnitsDialect.h"

#include "mlir/InitAllDialects.h"
#include "mlir/InitAllPasses.h"
#include "mlir/Pass/PassOptions.h"
#include "mlir/Pass/PassRegistry.h"
#include "mlir/Tools/mlir-opt/MlirOptMain.h"
#include "mlir/Transforms/Passes.h"

void unitsToLLVMPipelineBuilder(mlir::OpPassManager &manager) {
  // Units
  manager.addPass(mlir::units::createUnitsToStandard());
  manager.addPass(mlir::createCanonicalizerPass());
}

int main(int argc, char **argv) {
  mlir::DialectRegistry registry;
  registry.insert<mlir::units::UnitsDialect>();
  mlir::registerAllDialects(registry);
  mlir::registerAllPasses();

  mlir::units::registerUnitsToStandardPasses();

  mlir::PassPipelineRegistration<>("units-to-llvm",
                                   "Run passes to lower units dialect to LLVM",
                                   unitsToLLVMPipelineBuilder);

  return mlir::asMainReturnCode(
      mlir::MlirOptMain(argc, argv, "Units Pass Driver", registry));
}
