#pragma once

#include <memory>
#include <string>

namespace mlir {
class ExecutionEngine;
}

namespace units::backend {

class CompiledFunction {
public:
  CompiledFunction(std::unique_ptr<mlir::ExecutionEngine> engine,
                   std::string entryPoint);

  ~CompiledFunction();

  CompiledFunction(const CompiledFunction &) = delete;
  CompiledFunction &operator=(const CompiledFunction &) = delete;

  double invoke(double argument) const;

private:
  std::unique_ptr<mlir::ExecutionEngine> engine;
  std::string entryPoint;
};

} // namespace units::backend
