from types import FunctionType

from units.ast_parser import transform_ast
from units.driver import NativeBackend
from units.mlir_emit import emit_mlir


def verify[F: FunctionType](fn: F) -> F:
    backend = NativeBackend.default()
    fn_ast = transform_ast(fn)
    fn_ir = emit_mlir(fn_ast)
    backend.verify_mlir(fn_ir)
    return fn
