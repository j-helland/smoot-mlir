#pragma once

#include <memory>
#include <string>
#include <vector>

namespace mlir {
class ExecutionEngine;
}

namespace units::backend {

class CompiledFunction {
public:
  CompiledFunction(std::unique_ptr<mlir::ExecutionEngine> engine,
                   std::string entryPoint, std::size_t numArgs);

  ~CompiledFunction();

  CompiledFunction(const CompiledFunction &) = delete;
  CompiledFunction &operator=(const CompiledFunction &) = delete;

  double invoke(std::vector<double> argument) const;

private:
  std::unique_ptr<mlir::ExecutionEngine> engine;
  std::string entryPoint;
  std::size_t numArgs;
};

} // namespace units::backend
