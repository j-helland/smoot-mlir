#pragma once

#include <memory>

#include <mlir/IR/BuiltinOps.h>

#include "CompiledFunction.h"

namespace units::backend {

std::unique_ptr<CompiledFunction> compileMlir(mlir::ModuleOp module,
                                              const std::string &entrypoint);

} // namespace units::backend
