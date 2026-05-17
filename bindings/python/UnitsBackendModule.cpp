#include "Units/UnitsDialect.h"

#include <stdexcept>
#include <string>

#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/SMLoc.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/raw_os_ostream.h>
#include <llvm/Support/raw_ostream.h>

#include <mlir/Dialect/Func/IR/FuncOps.h>
#include <mlir/IR/Diagnostics.h>
#include <mlir/IR/DialectRegistry.h>
#include <mlir/IR/MLIRContext.h>
#include <mlir/IR/OwningOpRef.h>
#include <mlir/IR/Verifier.h>
#include <mlir/Parser/Parser.h>
#include <mlir/Support/LLVM.h>

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace {

class BackendError : public std::runtime_error {
public:
  using std::runtime_error::runtime_error;
};

std::string getDiagnosticText(const std::string &diagnostics,
                              const char *fallback) {
  if (!diagnostics.empty())
    return diagnostics;
  return fallback;
}

void verifyMlir(std::string const &text) {
  mlir::DialectRegistry registry;
  registry.insert<mlir::func::FuncDialect>();
  registry.insert<mlir::units::UnitsDialect>();

  mlir::MLIRContext context(registry);
  context.getOrLoadDialect<mlir::func::FuncDialect>();
  context.getOrLoadDialect<mlir::units::UnitsDialect>();

  llvm::SourceMgr sourceMgr;
  sourceMgr.AddNewSourceBuffer(
      llvm::MemoryBuffer::getMemBufferCopy(text, "<python-generated>"),
      llvm::SMLoc());

  std::string diagnostics;
  llvm::raw_string_ostream diagnosticsStream(diagnostics);
  mlir::SourceMgrDiagnosticHandler diagnosticHandler(sourceMgr, &context,
                                                     diagnosticsStream);

  mlir::OwningOpRef<mlir::ModuleOp> module =
      mlir::parseSourceFile<mlir::ModuleOp>(sourceMgr, &context);

  diagnosticsStream.flush();

  if (!module) {
    throw BackendError(
        getDiagnosticText(diagnostics, "failed to parse generated MLIR"));
  }

  if (mlir::failed(mlir::verify(module.get()))) {
    diagnosticsStream.flush();
    throw BackendError(
        getDiagnosticText(diagnostics, "failed to verify generated MLIR"));
  }
}

} // namespace

PYBIND11_MODULE(_units_backend, module) {
  py::register_exception<BackendError>(module, "BackendError");

  module.doc() = "Native MLIR backend bindings for the units frontend.";

  module.def("verify_mlir", &verifyMlir, py::arg("text"),
             "Parse and verify Units MLIR in-process.");
}
