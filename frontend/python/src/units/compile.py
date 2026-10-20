from types import FunctionType

from units import _units_backend
from units.ast_parser import transform_ast
from units.driver import NativeBackend
from units.mlir_emit import emit_mlir


def compile(fn: FunctionType) -> _units_backend.CompiledFunction:
    backend = NativeBackend.default()
    fn_ast = transform_ast(fn)
    fn_ir = emit_mlir(fn_ast)
    backend.verify_mlir(fn_ir)
    fn_compiled = backend.compile_mlir(fn_ir, entrypoint=fn.__name__)
    return fn_compiled
