#include <string>

#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/SMLoc.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/TargetSelect.h>
#include <llvm/Support/raw_os_ostream.h>
#include <llvm/Support/raw_ostream.h>

#include <mlir-c/IR.h>
#include <mlir-c/Support.h>
#include <mlir/Bindings/Python/NanobindAdaptors.h>
#include <mlir/CAPI/IR.h>
#include <mlir/Dialect/Func/IR/FuncOps.h>
#include <mlir/IR/Diagnostics.h>
#include <mlir/IR/DialectRegistry.h>
#include <mlir/IR/MLIRContext.h>
#include <mlir/IR/OwningOpRef.h>
#include <mlir/IR/Verifier.h>
#include <mlir/Parser/Parser.h>
#include <mlir/Support/LLVM.h>

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/unique_ptr.h>

#include "Units/UnitsDialect.h"
#include "BackendError.h"
#include "CompiledFunction.h"
#include "Compiler.h"
#include "bindings/c/UnitsDialect.h"

namespace nb = nanobind;

namespace units::backend {

std::string getDiagnosticText(const std::string &diagnostics,
                              const char *fallback) {
  if (!diagnostics.empty())
    return diagnostics;
  return fallback;
}

} // namespace units::backend

NB_MODULE(_units_backend, module) {
  // Registers the Python exception type.
  // NOLINTNEXTLINE(bugprone-unused-raii,bugprone-throw-keyword-missing)
  nb::exception<units::backend::BackendError>(module, "BackendError");
  nb::class_<units::backend::CompiledFunction>(module, "CompiledFunction")
      .def("__call__", &units::backend::CompiledFunction::invoke);

  if (llvm::InitializeNativeTarget() ||
      llvm::InitializeNativeTargetAsmPrinter()) {
    throw units::backend::BackendError(
        "failed to initialize native code generation");
  }

  module.doc() = "Native MLIR backend bindings for the units frontend.";

  module.def(
      "compile_mlir",
      [](MlirModule input, const std::string &entrypoint) {
        return units::backend::compileMlir(unwrap(input), entrypoint);
      },
      nb::arg("module"), nb::arg("entrypoint"));

  module.def(
      "register_dialect",
      [](MlirContext context) {
        MlirDialectHandle handle = mlirGetDialectHandle__units__();
        mlirDialectHandleRegisterDialect(handle, context);
        mlirDialectHandleLoadDialect(handle, context);
      },
      nb::arg("context"));

  module.def(
      "quantity_type",
      [](MlirType elementType, const std::string &unitExpression) {
        return mlirUnitsQuantityTypeGet(
            elementType,
            mlirStringRefCreate(unitExpression.data(), unitExpression.size()));
      },
      nb::arg("element_type"), nb::arg("unit_expression"));
}
