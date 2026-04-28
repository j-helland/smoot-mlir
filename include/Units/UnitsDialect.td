include "mlir/IR/DialectBase.td"

def UnitsDialect : Dialect {
  let name = "units";
  let cppNamespace = "::units";

  let useDefaultTypePrinterParser = 1;

  let extraClassDeclaration = [{
    void registerTypes();
  }];
}

