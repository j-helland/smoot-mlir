from types import FunctionType
from typing import TYPE_CHECKING, TypeVar

from units.ast_parser import transform_ast
from units.driver import NativeBackend
from units.mlir_emit import emit_mlir

if TYPE_CHECKING:
    F = TypeVar("F", bound=FunctionType)


def verify(fn: F) -> F:
    backend = NativeBackend.default()
    fn_ast = transform_ast(fn)
    fn_ir = emit_mlir(fn_ast)
    backend.verify_mlir(fn_ir)
    return fn
