#include "Units/UnitsOps.h"
#include "Units/UnitsTypes.h"

#include "mlir/Dialect/Arith/IR/Arith.h"
#include "mlir/IR/BuiltinAttributes.h"
#include "mlir/IR/BuiltinDialect.h"
#include "mlir/IR/BuiltinOps.h"
#include "mlir/IR/DialectRegistry.h"
#include "mlir/IR/MLIRContext.h"
#include "mlir/IR/PatternMatch.h"
#include "mlir/Pass/Pass.h"
#include "mlir/Pass/PassRegistry.h"
#include "mlir/Support/LLVM.h"
#include "mlir/Support/TypeID.h"
#include "mlir/Transforms/DialectConversion.h"
#include "mlir/Transforms/GreedyPatternRewriteDriver.h"

namespace {
struct ConvertUnitsToArithPass
    : public mlir::PassWrapper<ConvertUnitsToArithPass,
                               mlir::OperationPass<mlir::ModuleOp>> {
  MLIR_DEFINE_EXPLICIT_INTERNAL_INLINE_TYPE_ID(ConvertUnitsToArithPass)

  llvm::StringRef getArgument() const final { return "convert-units-to-arith"; }
  llvm::StringRef getDescription() const final {
    return "Lower the units dialect to arith";
  }

  void runOnOperation() override;

  void getDependentDialects(mlir::DialectRegistry &registry) const override {
    registry.insert<mlir::arith::ArithDialect>();
  }
};
} // namespace

namespace {
struct ConstLowering : mlir::OpConversionPattern<units::ConstOp> {
  using OpConversionPattern::OpConversionPattern;

  mlir::LogicalResult
  matchAndRewrite(units::ConstOp op, OpAdaptor adaptor,
                  mlir::ConversionPatternRewriter &rewriter) const override {
    auto quantityType =
        llvm::cast<units::QuantityType>(op.getResult().getType());
    auto constant = mlir::arith::ConstantOp::create(
        rewriter, op.getLoc(), quantityType.getElementType(),
        op.getValueAttr());
    rewriter.replaceOp(op, constant.getResult());
    return mlir::success();
  }
};

struct MulLowering : mlir::OpConversionPattern<units::MulOp> {
  using OpConversionPattern::OpConversionPattern;

  mlir::LogicalResult
  matchAndRewrite(units::MulOp op, OpAdaptor adaptor,
                  mlir::ConversionPatternRewriter &rewriter) const override {
    auto quantityType =
        llvm::cast<units::QuantityType>(op.getResult().getType());
    auto mul = mlir::arith::MulFOp::create(rewriter, op.getLoc(),
                                           quantityType.getElementType(),
                                           adaptor.getLhs(), adaptor.getRhs());
    rewriter.replaceOp(op, mul.getResult());
    return mlir::success();
  }
};
} // namespace

void ConvertUnitsToArithPass::runOnOperation() {
  mlir::MLIRContext &context = getContext();

  mlir::TypeConverter converter;
  // noop on all "normal" types
  converter.addConversion([](mlir::Type type) { return type; });
  // !units.quantity<f64, *> -> f64
  converter.addConversion([](units::QuantityType type) -> mlir::Type {
    return type.getElementType();
  });

  mlir::RewritePatternSet patterns(&context);
  patterns.add<ConstLowering, MulLowering>(converter, &context);

  mlir::ConversionTarget target(context);
  target.addLegalDialect<mlir::arith::ArithDialect>();
  target.addLegalDialect<mlir::BuiltinDialect>();
  target.addIllegalDialect<units::UnitsDialect>();

  if (mlir::failed(mlir::applyFullConversion(getOperation(), target,
                                             std::move(patterns)))) {
    signalPassFailure();
  }
}

void registerConvertUnitsToArithPass() {
  mlir::PassRegistration<ConvertUnitsToArithPass>();
}
