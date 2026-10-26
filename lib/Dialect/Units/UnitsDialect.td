#ifndef LIB_DIALECT_UNITS_UNITSDIALECT_TD_
#define LIB_DIALECT_UNITS_UNITSDIALECT_TD_

include "mlir/IR/DialectBase.td"

def UnitsDialect : Dialect {
  let name = "units";
  let summary = "A dialect for scientific units.";
  let description = [{
    The units dialect defines types and operations for arithmetic expressions
    involving scientific units.
  }];

  let cppNamespace = "::mlir::units";

  let useDefaultTypePrinterParser = 1;
  let useDefaultAttributePrinterParser = 1;

  let extraClassDeclaration = [{
    void registerAttributes();
  }];
}

#endif // LIB_DIALECT_UNITS_UNITSDIALECT_TD_
