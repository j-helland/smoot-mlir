#include "Units/UnitsAlgebra.h"

#include "llvm/Support/Errc.h"
#include <string>
#include "units_rs.h"

namespace mlir::units::algebra {
namespace {

/**
 * Handle Rust core results propagated through the C ABI.
 */
llvm::Expected<std::string> takeResult(UnitsStringResult result) {
  if (result.ok) {
    const std::string value = result.value ? result.value : "";
    units_free_string(result.value);
    return value;
  }

  const std::string error =
      result.error ? result.error : "unknown units-rs error";
  units_free_string(result.error);

  return llvm::createStringError(llvm::errc::invalid_argument, "%s",
                                 error.c_str());
}

} // namespace

llvm::Expected<std::string> multiply(llvm::StringRef lhs, llvm::StringRef rhs) {
  const std::string lhsStorage = lhs.str();
  const std::string rhsStorage = rhs.str();
  return takeResult(units_mul(lhsStorage.c_str(), rhsStorage.c_str()));
}

llvm::Expected<std::string> add(llvm::StringRef lhs, llvm::StringRef rhs) {
  const std::string lhsStorage = lhs.str();
  const std::string rhsStorage = rhs.str();
  return takeResult(units_add_result(lhsStorage.c_str(), rhsStorage.c_str()));
}

} // namespace mlir::units::algebra
