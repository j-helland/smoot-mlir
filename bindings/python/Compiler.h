#pragma once

#include <memory>

#include "CompiledFunction.h"

namespace units::backend {

std::unique_ptr<CompiledFunction> compileMlir(const std::string &text,
                                              const std::string &entryPoint);

} // namespace units::backend
