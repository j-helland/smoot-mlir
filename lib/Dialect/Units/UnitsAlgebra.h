#pragma once

#include "llvm/ADT/StringRef.h"
#include "llvm/Support/Error.h"
#include <string>

namespace mlir::units::algebra {

llvm::Expected<std::string> multiply(llvm::StringRef lhs, llvm::StringRef rhs);

llvm::Expected<std::string> add(llvm::StringRef lhs, llvm::StringRef rhs);

} // namespace mlir::units::algebra
