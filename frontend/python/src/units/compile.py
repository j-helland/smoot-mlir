import functools
from types import FunctionType

from units import _units_backend
from units.ast_parser import transform_ast
from units.driver import NativeBackend
from units.mlir_emit import emit_mlir


# TODO(jwh): identify a reasonable cache size or make caller configurable
@functools.lru_cache(maxsize=32)
def compile(fn: FunctionType) -> _units_backend.CompiledFunction:
    """JIT compile the decorated function, replacing it with native code.

    Units are stripped away, incurring no performance overhead after initial compilation.

    Warning
    -------
    Avoid decorating temporary functions defined inside loops or other Python scopes.
    Compiled functions are cached using a hash of the function, which means that unnecessary compilations will occur in such cases.
    """
    backend = NativeBackend.default()
    fn_ast = transform_ast(fn)
    mlir_module = emit_mlir(fn_ast)
    backend.verify_mlir(mlir_module)
    fn_compiled = backend.compile_mlir(mlir_module, entrypoint=fn.__name__)
    return fn_compiled
