#include <utility>

#include <llvm/Support/Error.h>
#include <mlir/ExecutionEngine/ExecutionEngine.h>

#include "BackendError.h"
#include "CompiledFunction.h"

namespace units::backend {

CompiledFunction::CompiledFunction(
    std::unique_ptr<mlir::ExecutionEngine> engine, std::string entryPoint)
    : engine(std::move(engine)), entryPoint(std::move(entryPoint)) {}

CompiledFunction::~CompiledFunction() = default;

double CompiledFunction::invoke(double argument) const {
  double output = 0.0;

  if (auto error = engine->invoke(entryPoint, argument,
                                  mlir::ExecutionEngine::result(output))) {
    throw BackendError(llvm::toString(std::move(error)));
  }

  return output;
}

} // namespace units::backend
