from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from units import UnitsCompileError
from units.annotations import QuantityTypeInfo, Unit
from units.ir import Binary, Expr, Function, Name, Node, Operator, Return, Stmt


@dataclass(frozen=True, slots=True)
class MlirValue:
    name: str
    type: QuantityTypeInfo | None = None

    def __str__(self) -> str:
        return self.name


MlirSymbolTableType: TypeAlias = dict[str, MlirValue]


def emit_mlir(node: Node) -> str:
    """Emit Units MLIR dialect."""
    emitter = MlirEmitter()
    return emitter.emit_module(node)


@dataclass(slots=True)
class MlirEmitter:
    _next_ssa_id: int = 0
    _lines: list[str] = field(default_factory=list)
    _values: dict[Expr, str] = field(default_factory=dict)

    def emit_module(self, node: Node) -> str:
        self._lines.append("module {")
        self.emit_node(node)
        self._lines.append("}")
        return "\n".join(self._lines) + "\n"

    def emit_node(self, node: Node) -> None:
        match node:
            case Function():
                self.emit_function(node)
            case _:
                raise UnitsCompileError from NotImplementedError(type(node))

    def emit_function(self, function: Function) -> None:
        sig = function.signature
        params = ", ".join(
            f"%{name}: {emit_quantity_type(type_info)}"
            for name, type_info in sig.parameters
        )

        self._lines.append(
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
            self._lines.append(f"    {value}")
        self._lines.append("  }")

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
                raise TypeError(msg)

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

                result_name = self.get_next_ssa_id()

                self._lines.append(
                    f"    {result_name} = {mlir_op} {lhs_val}, {rhs_val}"
                )
                self._lines.append(
                    f"      : {emit_quantity_type(lhs_type)}, {emit_quantity_type(rhs_type)}"
                )

                return MlirValue(result_name)

            case _:
                msg = f"unsupported IR expression: {expr!r}"
                raise TypeError(msg)

    def get_next_ssa_id(self) -> str:
        value = f"%{self._next_ssa_id}"
        self._next_ssa_id += 1
        return value


def emit_quantity_type(type_info: QuantityTypeInfo) -> str:
    return f"!units.quantity<{emit_element_type(type_info.element)}, {emit_unit_attr(type_info.unit)}>"


def emit_element_type(element: str) -> str:
    if element == "f64":
        return "f64"

    msg = f"unsupported element type: {element!r}"
    raise TypeError(msg)


def emit_unit_attr(unit: Unit) -> str:
    return f"""#units.unit<"{unit.expression}">"""


def emit_operator(op: Operator) -> str:
    match op:
        case Operator.add:
            return "units.add"
        case Operator.mul:
            return "units.mul"
        case _:
            raise NotImplementedError(op)


def require_type(value: MlirValue) -> QuantityTypeInfo:
    if value.type is None:
        msg = f"cannot emit operand `{value.name}` without a known type"
        raise TypeError(msg)
    return value.type
