#include "Units/UnitsAttrs.h"

#include "mlir/IR/MLIRContext.h"
#include "gtest/gtest.h"

namespace {

class UnitAttrTest : public ::testing::Test {
protected:
  UnitAttrTest() {
    registry.insert<mlir::units::UnitsDialect>();
    context.appendDialectRegistry(registry);
    context.loadDialect<mlir::units::UnitsDialect>();
  }

  mlir::DialectRegistry registry;
  mlir::MLIRContext context;
};

TEST_F(UnitAttrTest, StoresUnitExpression) {
  auto unit = mlir::units::UnitAttr::get(&context, "meter / second");
  EXPECT_EQ(unit.getExpression(), "meter / second");
}

TEST_F(UnitAttrTest, DistinguishesDifferentExpressions) {
  auto meter = mlir::units::UnitAttr::get(&context, "meter");
  auto second = mlir::units::UnitAttr::get(&context, "second");
  EXPECT_NE(meter, second);
}

} // namespace
