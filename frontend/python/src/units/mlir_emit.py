from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, TypeAlias

from units import UnitsCompileError
from units.annotations import QuantityTypeInfo, Unit
from units.diagnostics import Diagnostic
from units.ir import Binary, Expr, Function, Name, Node, Operator, Return, Stmt
from units.span import SourceSpan


@dataclass(frozen=True, slots=True)
class MlirValue:
    name: str
    type: QuantityTypeInfo | None = None

    def __str__(self) -> str:
        return self.name


MlirSymbolTableType: TypeAlias = dict[str, MlirValue]
LineMapType: TypeAlias = dict[int, SourceSpan]


@dataclass(frozen=True, slots=True)
class GeneratedModule:
    text: str
    line_map: Mapping[int, SourceSpan]


def emit_mlir(node: Node) -> GeneratedModule:
    """Emit Units MLIR dialect."""
    emitter = MlirEmitter()
    return emitter.emit_module(node)


@dataclass(slots=True)
class MlirEmitter:
    _next_ssa_id: int = 0
    _lines: list[str] = field(default_factory=list)
    _line_map: LineMapType = field(default_factory=dict)
    _values: dict[Expr, str] = field(default_factory=dict)

    def emit_module(self, node: Node) -> GeneratedModule:
        self._append_line("module {")
        self.emit_node(node)
        self._append_line("}")

        return GeneratedModule(
            text="\n".join(self._lines) + "\n",
            line_map=dict(self._line_map),
        )

    def emit_node(self, node: Node) -> None:
        match node:
            case Function():
                self.emit_function(node)
            case _:
                msg = f"unsupported IR node type `{node!r}`"
                raise UnitsCompileError(Diagnostic.emit(msg, node.span))

    def emit_function(self, function: Function) -> None:
        sig = function.signature
        params = ", ".join(
            f"%{name}: {emit_quantity_type(type_info)}"
            for name, type_info in sig.parameters
        )

        self._append_line(
            f"  func.func @{sig.name}({params}) -> {emit_quantity_type(sig.result)} {{"
        )

        symbols = {
            name: MlirValue(name=f"%{name}", type=type_info)
            for name, type_info in sig.parameters
        }
        for stmt in function.body:
            value = self.emit_stmt(
                stmt,
                symbols=symbols,
                return_type=function.signature.result,
            )
            self._append_line(f"    {value}")
        self._append_line("  }")

    def emit_stmt(
        self,
        stmt: Stmt,
        *,
        symbols: MlirSymbolTableType,
        return_type: QuantityTypeInfo,
    ) -> str:
        match stmt:
            case Return(expr=expr):
                value_mlir = self.emit_expr(expr, symbols)
                return f"return {value_mlir}: {emit_quantity_type(return_type)}"

            case _:
                msg = f"unsupported statement: {stmt}"
                raise UnitsCompileError(Diagnostic.emit(msg, stmt.span))

    def emit_expr(self, expr: Expr, symbols: MlirSymbolTableType) -> MlirValue:
        match expr:
            case Name(name=name):
                return symbols[name]

            case Binary(op=op, lhs=lhs, rhs=rhs):
                mlir_op = emit_operator(op)
                lhs_val = self.emit_expr(lhs, symbols)
                rhs_val = self.emit_expr(rhs, symbols)

                lhs_type = require_type(lhs_val)
                rhs_type = require_type(rhs_val)

                result_name = self._get_next_ssa_id()

                self._append_line(f"    {result_name} = {mlir_op} {lhs_val}, {rhs_val}")
                self._append_line(
                    f"      : {emit_quantity_type(lhs_type)}, {emit_quantity_type(rhs_type)}"
                )

                return MlirValue(result_name)

            case _:
                msg = f"unsupported IR expression: {expr!r}"
                raise UnitsCompileError(Diagnostic.emit(msg))

    def _get_next_ssa_id(self) -> str:
        value = f"%{self._next_ssa_id}"
        self._next_ssa_id += 1
        return value

    def _append_line(self, line: str, span: SourceSpan | None = None) -> None:
        self._lines.append(line)
        if span is not None:
            self._line_map[len(self._lines)] = span


def emit_quantity_type(type_info: QuantityTypeInfo) -> str:
    return f"!units.quantity<{emit_element_type(type_info.element)}, {emit_unit_attr(type_info.unit)}>"


def emit_element_type(element: str) -> str:
    if element == "f64":
        return "f64"

    msg = f"unsupported element type: {element!r}"
    raise UnitsCompileError(Diagnostic.emit(msg))


def emit_unit_attr(unit: Unit) -> str:
    return f"""#units.unit<"{unit.expression}">"""


def emit_operator(op: Operator) -> str:
    match op:
        case Operator.add:
            return "units.add"
        case Operator.mul:
            return "units.mul"
        case _:
            msg = f"unsupported operator `{op!r}`"
            raise UnitsCompileError(Diagnostic.emit(msg))


def require_type(value: MlirValue) -> QuantityTypeInfo:
    if value.type is None:
        msg = f"cannot emit operand `{value.name}` without a known type"
        raise UnitsCompileError(Diagnostic.emit(msg))
    return value.type
