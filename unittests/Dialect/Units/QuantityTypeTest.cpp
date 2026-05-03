#include "Units/UnitsAttrs.h"
#include "Units/UnitsDialect.h"
#include "Units/UnitsTypes.h"

#include "gtest/gtest.h"
#include <mlir/IR/BuiltinTypes.h>
#include <mlir/IR/DialectRegistry.h>
#include <mlir/IR/MLIRContext.h>

namespace {

class QuantityTypeTest : public ::testing::Test {
protected:
  QuantityTypeTest() {
    registry.insert<mlir::units::UnitsDialect>();
    context.appendDialectRegistry(registry);
    context.loadDialect<mlir::units::UnitsDialect>();
  }

  mlir::DialectRegistry registry;
  mlir::MLIRContext context;
};

TEST_F(QuantityTypeTest, CanonicalizesDimensionality) {
  auto quantity = mlir::units::QuantityType::get(
      &context, mlir::Float64Type{}, mlir::units::UnitAttr::get(&context, {1, 0}));
  auto expected = mlir::units::UnitAttr::get(&context, {1});

  ASSERT_EQ(quantity.getUnit(), expected);
}

} // namespace
