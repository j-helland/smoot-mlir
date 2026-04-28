#include "Units/UnitsDialect.h"

#include "mlir/IR/DialectRegistry.h"
#include "mlir/Tools/Plugins/DialectPlugin.h"
#include "mlir/Tools/Plugins/PassPlugin.h"
#include "llvm/Config/llvm-config.h"
#include "llvm/Support/Compiler.h"

extern "C" LLVM_ATTRIBUTE_WEAK mlir::DialectPluginLibraryInfo
mlirGetDialectPluginInfo() {
  return {
      MLIR_PLUGIN_API_VERSION,
      "UnitsDialect",
      LLVM_VERSION_STRING,
      [](mlir::DialectRegistry *registry) {
        registry->insert<units::UnitsDialect>();
      },
  };
}
