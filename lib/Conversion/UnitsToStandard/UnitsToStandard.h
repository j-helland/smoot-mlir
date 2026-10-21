#pragma once

#include <mlir/Pass/PassRegistry.h>

namespace mlir {
class Pass;

namespace units {

#define GEN_PASS_DECL
#include "lib/Conversion/UnitsToStandard/UnitsToStandard.h.inc"

#define GEN_PASS_REGISTRATION
#include "lib/Conversion/UnitsToStandard/UnitsToStandard.h.inc"

} // namespace units
} // namespace mlir
