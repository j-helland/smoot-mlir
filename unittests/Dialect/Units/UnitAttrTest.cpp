#include "Units/UnitsAttrs.h"
#include "Units/UnitsDialect.h"

#include "mlir/IR/MLIRContext.h"
#include "llvm/ADT/ArrayRef.h"
#include "gtest/gtest.h"
#include <cstdint>

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

TEST_F(UnitAttrTest, CanonicalizesTrailingZeros) {
  auto canonical = mlir::units::UnitAttr::get(&context, {1});
  auto trailingZero = mlir::units::UnitAttr::get(&context, {1, 0});
  auto manyTrailingZeros = mlir::units::UnitAttr::get(&context, {1, 0, 0});

  EXPECT_EQ(canonical, trailingZero);
  EXPECT_EQ(canonical, manyTrailingZeros);
  EXPECT_EQ(canonical.getDims(), llvm::ArrayRef<int64_t>({1}));
}

TEST_F(UnitAttrTest, CanonicalizesDimensionlessToEmptyDims) {
  auto empty = mlir::units::UnitAttr::get(&context, {});
  auto oneZero = mlir::units::UnitAttr::get(&context, {0});
  auto manyZeros = mlir::units::UnitAttr::get(&context, {0, 0});

  EXPECT_EQ(empty, oneZero);
  EXPECT_EQ(empty, manyZeros);
  EXPECT_TRUE(empty.getDims().empty());
}

TEST_F(UnitAttrTest, PreservesNonTrailingZeros) {
  auto unit = mlir::units::UnitAttr::get(&context, {1, 0, -1});

  ASSERT_EQ(unit.getDims(), llvm::ArrayRef<int64_t>({1, 0, -1}));
}

} // namespace
