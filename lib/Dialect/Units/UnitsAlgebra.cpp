#include "Units/UnitsAlgebra.h"
#include "units_rs.h"

#include <llvm/Support/Errc.h>
#include <llvm/Support/Error.h>

#include <string>
#include <utility>

namespace mlir::units::algebra {

namespace {

llvm::Error takeError(char *error) {
  const std::string message = error ? error : "unknown units-rs error";
  units_free_string(error);
  return llvm::createStringError(llvm::errc::invalid_argument, "%s",
                                 message.c_str());
}

llvm::Expected<Unit> takeUnitResult(Units_UnitResult result) {
  if (result.ok) {
    return Unit(result.value);
  }
  return takeError(result.error);
}

llvm::Expected<std::string> takeStringResult(Units_StringResult result) {
  if (result.ok) {
    const std::string value = result.value ? result.value : "";
    units_free_string(result.value);
    return value;
  }
  return takeError(result.error);
}

llvm::Expected<double> takeF64Result(Units_F64Result result) {
  if (result.ok) {
    return result.value;
  }
  return takeError(result.error);
}

} // namespace

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

llvm::Expected<bool> Unit::isCompatibleWith(const Unit &other) const {
  auto result = units_is_compatible_with(this->get(), other.get());
  if (result.ok) {
    return result.value;
  }
  return takeError(result.error);
}

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

llvm::Expected<double> conversionFactor(const Unit &from, const Unit &to) {
  auto result = units_conversion_factor(from.get(), to.get());
  return takeF64Result(result);
}

} // namespace mlir::units::algebra
