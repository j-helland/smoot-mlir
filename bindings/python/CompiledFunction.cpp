#include <string_view>
#include <utility>

#include <llvm/ADT/ArrayRef.h>
#include <llvm/ADT/SmallVector.h>
#include <llvm/Support/Error.h>
#include <mlir/ExecutionEngine/ExecutionEngine.h>

#include "BackendError.h"
#include "CompiledFunction.h"

namespace units::backend {

namespace {

/**
 * MLIR wrapper naming convention that we need to match.
 */
constexpr std::string_view g_cInterfacePrefix = "_mlir_ciface_";

} // namespace

CompiledFunction::CompiledFunction(
    std::unique_ptr<mlir::ExecutionEngine> engine, std::string entryPoint,
    std::size_t numArgs)
    : engine(std::move(engine)), entryPoint(std::move(entryPoint)),
      numArgs(numArgs) {}

CompiledFunction::~CompiledFunction() = default;

double CompiledFunction::invoke(std::vector<double> argument) const {
  double output = 0.0;

  if (argument.size() != numArgs) {
    throw BackendError("Invalid number of arguments. Expected " +
                       std::to_string(numArgs) + " arguments, got " +
                       std::to_string(argument.size()));
  }

  llvm::SmallVector<void *> packed;
  packed.reserve(argument.size() + 1);
  for (double &value : argument) {
    packed.push_back(&value);
  }
  packed.push_back(&output);

  if (auto error = engine->invokePacked(
          std::string(g_cInterfacePrefix) + entryPoint, packed)) {
    throw BackendError(llvm::toString(std::move(error)));
  }

  return output;
}

} // namespace units::backend
