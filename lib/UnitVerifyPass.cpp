#include "mlir/Dialect/Arith/IR/Arith.h"
#include "mlir/IR/Builders.h"
#include "mlir/IR/BuiltinAttributes.h"
#include "mlir/IR/BuiltinOps.h"
#include "mlir/IR/Operation.h"
#include "mlir/Pass/Pass.h"
#include "mlir/Pass/PassRegistry.h"
#include "mlir/Support/LLVM.h"
#include "mlir/Support/TypeID.h"
#include "mlir/Tools/Plugins/PassPlugin.h"
#include "llvm/Config/llvm-config.h"
#include "llvm/Support/Compiler.h"
#include <memory>

using mlir::Operation;
using mlir::Pass;
using mlir::PassRegistration;
using mlir::StringAttr;
using mlir::StringRef;

namespace {
struct UnitVerifyPass
    : public mlir::PassWrapper<UnitVerifyPass,
                               mlir::OperationPass<mlir::ModuleOp>> {

  MLIR_DEFINE_EXPLICIT_INTERNAL_INLINE_TYPE_ID(UnitVerifyPass)

  StringRef getArgument() const final { return "verify-units"; }

  StringRef getDescription() const final {
    return "Verify unit annotations on arithmetic operations";
  }

  void runOnOperation() override {
    mlir::ModuleOp module = getOperation();

    module->walk([&](Operation *op) {
      if (auto add = mlir::dyn_cast<mlir::arith::AddFOp>(op)) {
        auto lhs = op->getAttrOfType<StringAttr>("lhs_unit");
        auto rhs = op->getAttrOfType<StringAttr>("rhs_unit");

        if (lhs && rhs && lhs != rhs) {
          op->emitOpError()
              << "cannot add values with units `" << lhs.getValue() << "` and `"
              << rhs.getValue() << "`";
          this->signalPassFailure();
        }
      }

      if (auto mul = mlir::dyn_cast<mlir::arith::MulFOp>(op)) {
        auto lhs = op->getAttrOfType<StringAttr>("lhs_unit");
        auto rhs = op->getAttrOfType<StringAttr>("rhs_unit");

        if (lhs && rhs) {
          // dumb hard-coded condition for PoC
          if (lhs.getValue() == "m/s" && rhs.getValue() == "s") {
            // OK
          }
        }
      }
    });
  }
};
} // namespace

std::unique_ptr<Pass> createUnitVerifyPass() {
  return std::make_unique<UnitVerifyPass>();
}

static void registerUnitVerifyPass() { PassRegistration<UnitVerifyPass>(); }

extern "C" LLVM_ATTRIBUTE_WEAK mlir::PassPluginLibraryInfo
mlirGetPassPluginInfo() {
  return {
      MLIR_PLUGIN_API_VERSION,
      "UnitVerifyPass",
      LLVM_VERSION_STRING,
      []() { registerUnitVerifyPass(); },
  };
}
