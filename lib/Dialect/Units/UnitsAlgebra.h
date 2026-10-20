#pragma once

#include <llvm/ADT/StringRef.h>
#include <llvm/Support/Error.h>

#include <string>

struct Units_Unit;

namespace mlir::units::algebra {

class Unit {
public:
  explicit Unit(Units_Unit *unit);
  ~Unit();

  Unit(Unit &&other) noexcept;
  Unit &operator=(Unit &&other) noexcept;

  Unit(const Unit &) = delete;
  Unit &operator=(const Unit &) = delete;

  const Units_Unit *get() const { return unit; }

private:
  Units_Unit *unit = nullptr;
};

llvm::Expected<Unit> parse(llvm::StringRef expression);

llvm::Expected<Unit> multiply(const Unit &lhs, const Unit &rhs);

llvm::Expected<Unit> add(const Unit &lhs, const Unit &rhs);

llvm::Expected<std::string> format(const Unit &unit);

} // namespace mlir::units::algebra
