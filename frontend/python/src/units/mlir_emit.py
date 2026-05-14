from __future__ import annotations

from dataclasses import dataclass, field

from units.annotations import QuantityTypeInfo, UnitInfo
from units.ir import Binary, Expr, Function, Name, Operator, Return, Stmt


def emit_module(function: Function) -> str:
    emitter = MlirEmitter()
    return emitter.emit_module(function)


@dataclass(slots=True)
class MlirEmitter:
    next_ssa_id: int = 0
    lines: list[str] = field(default_factory=list)
    values: dict[Expr, str] = field(default_factory=dict)

    def emit_module(self, function: Function) -> str:
        self.lines.append("module {")
        self.emit_function(function)
        self.lines.append("}")
        return "\n".join(self.lines) + "\n"

    def emit_function(self, function: Function) -> None:
        sig = function.signature
        params = ", ".join(
            f"%{name}: {emit_quantity_type(type_info)}"
            for name, type_info in sig.parameters
        )

        self.lines.append(
            f"  func.func @{sig.name}({params}) -> {emit_quantity_type(sig.result)} {{"
        )

        env = {name: f"%{name}" for name, _ in sig.parameters}
        for stmt in function.body:
            value = self.emit_stmt(stmt, env)
            self.lines.append(f"    {value}")
        self.lines.append("  }")

    def emit_stmt(self, stmt: Stmt, env: dict[str, str]) -> str:
        match stmt:
            case Return(expr=expr):
                value_mlir = self.emit_expr(expr, env)
                return f"return {value_mlir}: {emit_quantity_type(expr.type)}"

            case _:
                msg = f"unsupported statement: {stmt}"
                raise TypeError(msg)

    def emit_expr(self, expr: Expr, env: dict[str, str]) -> str:
        match expr:
            case Name(name=name):
                return env[name]

            case Binary(op=op, lhs=lhs, rhs=rhs, type=type_info):
                mlir_op = emit_operator(op)
                lhs_val = self.emit_expr(lhs, env)
                rhs_val = self.emit_expr(rhs, env)
                result_val = self.get_next_ssa_id()

                self.lines.append(f"    {result_val} = {mlir_op} {lhs_val}, {rhs_val}")
                self.lines.append(
                    f"      : {emit_quantity_type(lhs.type)}, {emit_quantity_type(rhs.type)}"
                )
                self.lines.append(f"      -> {emit_quantity_type(type_info)}")

                return result_val

            case _:
                msg = f"unsupported IR expression: {expr!r}"
                raise TypeError(msg)

    def get_next_ssa_id(self) -> str:
        value = f"%{self.next_ssa_id}"
        self.next_ssa_id += 1
        return value


def emit_quantity_type(type_info: QuantityTypeInfo) -> str:
    return f"!units.quantity<{emit_element_type(type_info.element)}, {emit_unit_attr(type_info.unit)}>"


def emit_element_type(element: str) -> str:
    if element == "f64":
        return "f64"

    msg = f"unsupported element type: {element!r}"
    raise TypeError(msg)


def emit_unit_attr(unit: UnitInfo) -> str:
    dims_str = ", ".join(str(dim) for dim in unit.dims)
    return f"#units.unit<dims = [{dims_str}]>"


def emit_operator(op: Operator) -> str:
    match op:
        case Operator.add:
            return "units.add"
        case Operator.mul:
            return "units.mul"
        case _:
            raise NotImplementedError(op)
