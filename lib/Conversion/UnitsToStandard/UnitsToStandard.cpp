#include "lib/Conversion/UnitsToStandard/UnitsToStandard.h"
#include "Units/UnitsOps.h"
#include "Units/UnitsTypes.h"

#include "mlir/Dialect/Arith/IR/Arith.h"
#include "mlir/Dialect/SCF/IR/SCF.h"
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

namespace mlir::units {

#define GEN_PASS_DEF_UNITSTOSTANDARD
#include "lib/Conversion/UnitsToStandard/UnitsToStandard.h.inc"

namespace {
struct UnitsToStandardPass
    : public impl::UnitsToStandardBase<UnitsToStandardPass> {
  using Base::Base;
  void runOnOperation() override;
};
} // namespace

namespace {
struct ConstLowering : mlir::OpConversionPattern<ConstOp> {
  using OpConversionPattern::OpConversionPattern;

  mlir::LogicalResult
  matchAndRewrite(ConstOp op, OpAdaptor adaptor,
                  mlir::ConversionPatternRewriter &rewriter) const override {
    auto quantityType = llvm::cast<QuantityType>(op.getResult().getType());
    auto constant = mlir::arith::ConstantOp::create(
        rewriter, op.getLoc(), quantityType.getElementType(),
        op.getValueAttr());
    rewriter.replaceOp(op, constant.getResult());
    return mlir::success();
  }
};

struct MulLowering : mlir::OpConversionPattern<MulOp> {
  using OpConversionPattern::OpConversionPattern;

  mlir::LogicalResult
  matchAndRewrite(MulOp op, OpAdaptor adaptor,
                  mlir::ConversionPatternRewriter &rewriter) const override {
    auto quantityType = llvm::cast<QuantityType>(op.getResult().getType());
    auto mul = mlir::arith::MulFOp::create(rewriter, op.getLoc(),
                                           quantityType.getElementType(),
                                           adaptor.getLhs(), adaptor.getRhs());
    rewriter.replaceOp(op, mul.getResult());
    return mlir::success();
  }
};

struct AddLowering : mlir::OpConversionPattern<AddOp> {
  using OpConversionPattern::OpConversionPattern;

  mlir::LogicalResult
  matchAndRewrite(AddOp op, OpAdaptor adaptor,
                  mlir::ConversionPatternRewriter &rewriter) const override {
    auto quantityType = llvm::cast<QuantityType>(op.getResult().getType());
    auto add = mlir::arith::AddFOp::create(rewriter, op.getLoc(),
                                           quantityType.getElementType(),
                                           adaptor.getLhs(), adaptor.getRhs());

    rewriter.replaceOp(op, add.getResult());
    return mlir::success();
  }
};
} // namespace

void UnitsToStandardPass::runOnOperation() {
  mlir::MLIRContext &context = getContext();

  mlir::TypeConverter converter;
  // noop on all "normal" types
  converter.addConversion([](mlir::Type type) { return type; });
  // !units.quantity<f64, *> -> f64
  converter.addConversion(
      [](QuantityType type) -> mlir::Type { return type.getElementType(); });

  mlir::RewritePatternSet patterns(&context);
  patterns.add<ConstLowering, MulLowering, AddLowering>(converter, &context);

  mlir::ConversionTarget target(context);
  target.addLegalDialect<mlir::arith::ArithDialect>();
  target.addLegalDialect<mlir::BuiltinDialect>();
  target.addIllegalDialect<UnitsDialect>();

  if (mlir::failed(mlir::applyFullConversion(getOperation(), target,
                                             std::move(patterns)))) {
    signalPassFailure();
  }
}

} // namespace mlir::units
