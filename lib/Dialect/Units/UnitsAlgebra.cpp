#include "Units/UnitsAlgebra.h"

#include "llvm/Support/Errc.h"
#include <llvm/Support/Error.h>
#include <string>
#include <utility>
#include "units_rs.h"

namespace mlir::units::algebra {

Unit::Unit(Units_Unit *unit) : unit(unit) {}

Unit::~Unit() {
  if (unit)
    units_free_unit(unit);
}

Unit::Unit(Unit &&other) noexcept : unit(std::exchange(other.unit, nullptr)) {}

Unit &Unit::operator=(Unit &&other) noexcept {
  if (this == &other)
    return *this;

  if (unit)
    units_free_unit(unit);

  unit = std::exchange(other.unit, nullptr);
  return *this;
}

namespace {

llvm::Expected<Unit> takeUnitResult(Units_UnitResult result) {
  if (result.ok)
    return Unit(result.value);

  const std::string error =
      result.error ? result.error : "unknown units-rs error";
  units_free_string(result.error);
  return llvm::createStringError(llvm::errc::invalid_argument, "%s",
                                 error.c_str());
}

llvm::Expected<std::string> takeStringResult(Units_StringResult result) {
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

llvm::Expected<Unit> parse(llvm::StringRef expression) {
  const std::string storage = expression.str();
  auto result = units_parse_unit(storage.c_str());
  return takeUnitResult(result);
}

llvm::Expected<Unit> multiply(const Unit &lhs, const Unit &rhs) {
  auto result = units_mul(lhs.get(), rhs.get());
  return takeUnitResult(result);
}

llvm::Expected<Unit> add(const Unit &lhs, const Unit &rhs) {
  auto result = units_add(lhs.get(), rhs.get());
  return takeUnitResult(result);
}

llvm::Expected<std::string> format(const Unit &unit) {
  auto result = units_format_unit(unit.get());
  return takeStringResult(result);
}

} // namespace mlir::units::algebra
