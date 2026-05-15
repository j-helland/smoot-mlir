from units.ast_parser import transform_ast
from units.mlir_emit import emit_mlir
from types import FunctionType
from units.driver import UnitsOpt
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    F = TypeVar("F", bound=FunctionType)


def verify(fn: F) -> F:
    units_opt = UnitsOpt.default()
    fn_ast = transform_ast(fn)
    fn_ir = emit_mlir(fn_ast)
    units_opt.run_units_opt(fn_ir)
    return fn
