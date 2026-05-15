from units.mlir_emit import emit_module
from types import FunctionType
from units.ast_parser import lower_function
from units.driver import UnitsOpt
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    F = TypeVar("F", bound=FunctionType)


def verify(fn: F) -> F:
    units_opt = UnitsOpt.default()
    fn_ast = lower_function(fn)
    fn_ir = emit_module(fn_ast)
    units_opt.run_units_opt(fn_ir)
    return fn
