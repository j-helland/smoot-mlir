from __future__ import annotations

from dataclasses import dataclass

from mlir import ir
from mlir.dialects import arith, func, scf

from units import _units_backend
from units.annotations import QuantityTypeInfo
from units.diagnostics import Diagnostic, UnitsCompileError
from units.dialects import units as units_ops
from units.ir import (
    Assign,
    Binary,
    Constant,
    Convert,
    Expr,
    For,
    Function,
    Name,
    Node,
    Operator,
    Range,
    Return,
    Stmt,
)
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

            case For(iterable=Range() as bounds) as loop:
                self.emit_range_loop(loop, bounds, symbols)

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

            case Convert(value=value, target=target):
                input = self.emit_expr(value, symbols)

                # TODO(jwh): handle non-f64 types or push down into backend
                result = lower_quantity_type(
                    QuantityTypeInfo(element="f64", unit=target)
                )

                return units_ops.ConvertOp(
                    result=result,
                    input=input,
                ).result

            case _:
                msg = f"unsupported IR expression: {expr!r}"
                raise UnitsCompileError(Diagnostic.emit(msg))

    def emit_range_loop(
        self,
        loop: For,
        bounds: Range,
        symbols: MlirSymbolTableType,
    ) -> None:
        lower = emit_index_constant(bounds.start)
        upper = emit_index_constant(bounds.stop)
        step = emit_index_constant(bounds.step)

        # Assignments that must be carried across loop iterations in a yield call.
        # See <https://mlir.llvm.org/docs/Dialects/SCFDialect/#scffor-scfforop>
        assigned = get_assigned_names(loop.body)
        carried = [name for name in symbols if name in assigned]
        initial_values = [symbols[name] for name in carried]

        op = scf.ForOp(
            lower,
            upper,
            step,
            iter_args=initial_values,
            loc=lower_location(loop.span),
        )

        # Don't mutate outer symbols with symbols scoped to the loop body.
        # NOTE(jwh): This differs from normal Python semantics, which does not scope loop body symbols.
        body_symbols = symbols.copy()
        for name, arg in zip(carried, op.inner_iter_args, strict=True):
            body_symbols[name] = arg

        with ir.InsertionPoint(op.body):
            for stmt in loop.body:
                self.emit_stmt(stmt, symbols=body_symbols)

            scf.YieldOp(
                [body_symbols[name] for name in carried],
                loc=lower_location(loop.span),
            )

        for name, result in zip(carried, op.results, strict=True):
            symbols[name] = result


def get_assigned_names(body: tuple[Stmt, ...]) -> set[str]:
    names: set[str] = set()
    for stmt in body:
        match stmt:
            case Assign(name=name):
                names.add(name)
            case For(body=nested_body):
                names.update(get_assigned_names(nested_body))
    return names


def emit_index_constant(expr: Expr) -> ir.Value:
    match expr:
        case Constant(value=value) if type(value) is int:
            return arith.ConstantOp.create_index(
                value,
                loc=lower_location(expr.span),
            ).result
        case _:
            msg = "expected an integer loop bound"
            raise UnitsCompileError(Diagnostic.emit(msg, expr.span))


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
