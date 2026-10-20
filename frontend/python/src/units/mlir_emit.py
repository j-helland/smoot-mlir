from __future__ import annotations

from dataclasses import dataclass

from mlir import ir
from mlir.dialects import func

from units import _units_backend
from units.annotations import QuantityTypeInfo
from units.diagnostics import Diagnostic, UnitsCompileError
from units.dialects import units as units_ops
from units.ir import Assign, Binary, Expr, Function, Name, Node, Operator, Return, Stmt
from units.span import SourceSpan


@dataclass(frozen=True, slots=True)
class MlirValue:
    name: str
    type: QuantityTypeInfo | None = None

    def __str__(self) -> str:
        return self.name


type MlirSymbolTableType = dict[str, ir.Value]
type LineMapType = dict[int, SourceSpan]


def emit_mlir(node: Node) -> ir.Module:
    """Emit Units MLIR dialect."""
    with ir.Context() as ctx, ir.Location.unknown():
        _units_backend.register_dialect(ctx)

        module = ir.Module.create()
        with ir.InsertionPoint(module.body):
            try:
                MlirEmitter().emit_node(node)
            except ir.MLIRError as e:  # ty: ignore[unresolved-attribute] MLIR Python bindings dynamically add this type
                raise UnitsCompileError(
                    Diagnostic.emit("Failed to emit MLIR", span=node.span)
                ) from e

    return module


@dataclass(slots=True)
class MlirEmitter:
    def emit_node(self, node: Node) -> None:
        match node:
            case Function():
                self.emit_function(node)
            case _:
                msg = f"unsupported IR node type `{node!r}`"
                raise UnitsCompileError(Diagnostic.emit(msg, node.span))

    def emit_function(self, function: Function) -> None:
        sig = function.signature
        param_types = [lower_quantity_type(info) for _, info in sig.parameters]
        result_type = lower_quantity_type(sig.result)

        operation = func.FuncOp(
            sig.name,
            (param_types, [result_type]),
            loc=lower_location(function.span),
        )
        block = operation.add_entry_block()

        symbols = {
            name: value
            for (name, _), value in zip(sig.parameters, block.arguments, strict=True)
        }

        with ir.InsertionPoint(block):
            for stmt in function.body:
                self.emit_stmt(stmt, symbols=symbols)

    def emit_stmt(
        self,
        stmt: Stmt,
        *,
        symbols: MlirSymbolTableType,
    ) -> None:
        match stmt:
            case Assign(name=name, expr=expr, declared_type=None):
                symbols[name] = self.emit_expr(expr, symbols)

            case Return(expr=expr):
                value = self.emit_expr(expr, symbols)
                func.ReturnOp(
                    [value],
                    loc=lower_location(stmt.span),
                )

            case _:
                msg = f"unsupported statement: {stmt}"
                raise UnitsCompileError(Diagnostic.emit(msg, stmt.span))

    def emit_expr(self, expr: Expr, symbols: MlirSymbolTableType) -> ir.Value:
        match expr:
            case Name(name=name):
                return symbols[name]

            case Binary(op=op, lhs=lhs, rhs=rhs):
                lhs_val = self.emit_expr(lhs, symbols)
                rhs_val = self.emit_expr(rhs, symbols)
                match op:
                    case Operator.add:
                        operation = units_ops.AddOp(
                            lhs_val,
                            rhs_val,
                            loc=lower_location(expr.span),
                        )
                    case Operator.mul:
                        operation = units_ops.MulOp(
                            lhs_val,
                            rhs_val,
                            loc=lower_location(expr.span),
                        )
                    case _:
                        raise UnitsCompileError(
                            Diagnostic.emit(f"unsupported operator {op!r}", expr.span)
                        )
                return operation.result

            case _:
                msg = f"unsupported IR expression: {expr!r}"
                raise UnitsCompileError(Diagnostic.emit(msg))


def lower_quantity_type(info: QuantityTypeInfo) -> ir.Type:
    if info.element != "f64":
        raise UnitsCompileError(
            Diagnostic.emit(f"unsupported element type: {info.element!r}")
        )

    return _units_backend.quantity_type(
        ir.F64Type.get(),
        info.unit.expression,
    )


def lower_location(span: SourceSpan | None) -> ir.Location:
    if span is None:
        return ir.Location.unknown()

    return ir.Location.file(
        span.filename,
        span.line,
        span.column + 1,
    )
