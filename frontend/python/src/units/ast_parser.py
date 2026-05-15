from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import dataclass
from numbers import Number
from types import FunctionType
from typing import Callable, Final, TypeAlias

from units import Unit, UnitsCompileError
from units.annotations import (
    QuantityTypeInfo,
    parse_quantity_annotation,
)
from units.ir import (
    Assign,
    Binary,
    Constant,
    Expr,
    Function,
    Name,
    Node,
    Operator,
    Return,
    SourceSpan,
    Stmt,
)
from units.signatures import FunctionSignature


@dataclass(frozen=True, kw_only=True)
class Symbol:
    type: QuantityTypeInfo | None = None


SymbolTableType: TypeAlias = dict[str, Symbol]

UNKNOWN_SOURCE_FILE: Final[str] = "<unknown>"


def transform_ast(value: object) -> Node:
    match value:
        case FunctionType():
            return _transform_function(value)
        case _:
            raise UnitsCompileError from NotImplementedError(type(value))


def _transform_function(fn: FunctionType) -> Function:
    signature = FunctionSignature.extract(fn)
    function_def = _get_function_def(fn)
    filename = inspect.getsourcefile(fn) or UNKNOWN_SOURCE_FILE
    _, start_line = inspect.getsourcelines(fn)
    lineno_offset = start_line - 1  # inspect returns 1-based

    symbol_table = {
        name: Symbol(
            type=decl_type,
        )
        for name, decl_type in signature.parameters
    }
    span_ctx = SourceSpan.Ctx(filename=filename, lineno_offset=lineno_offset)
    ctx = _AstTransformCtx(
        symbol_table=symbol_table,
        span=span_ctx,
        globals=fn.__globals__,
    )

    body = _transform_body(function_def, ctx)
    return Function(
        signature=signature,
        body=body,
        span=SourceSpan.from_ast(function_def, span_ctx),
    )


def _get_function_def(fn: Callable) -> ast.FunctionDef:
    source = textwrap.dedent(inspect.getsource(fn))
    module = ast.parse(source)

    function_defs = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if len(function_defs) != 1:
        msg = "expected exactly one function definition"
        raise TypeError(msg)

    return function_defs[0]


@dataclass(frozen=True, slots=True, kw_only=True)
class _AstTransformCtx:
    symbol_table: SymbolTableType
    span: SourceSpan.Ctx
    globals: dict[str, object]


def _transform_body(
    function_def: ast.FunctionDef,
    ctx: _AstTransformCtx,
) -> tuple[Stmt, ...]:
    statements = tuple(_transform_stmt(stmt, ctx) for stmt in function_def.body)

    if not any(isinstance(statement, Return) for statement in statements):
        msg = "function must contain a return statement"
        raise TypeError(msg)

    return statements


def _transform_stmt(
    node: ast.stmt,
    ctx: _AstTransformCtx,
) -> Stmt:
    match node:
        case ast.Assign([ast.Name(id=name)], value, _):
            expr = _transform_expr(value, ctx)
            ctx.symbol_table[name] = Symbol(type=expr.type)
            return Assign(
                name=name,
                expr=expr,
                span=SourceSpan.from_ast(node=node, ctx=ctx.span),
            )

        case ast.AnnAssign(ast.Name(id=name), annotation, value, simple):
            if simple != 1:
                msg = "only simple annotated assignments are supported"
                raise TypeError(msg)

            if value is None:
                msg = "annotated assignments must include a value"
                raise TypeError(msg)

            decl_type = _transform_annotation(annotation, ctx)
            expr = _transform_expr(value, ctx)
            ctx.symbol_table[name] = Symbol(type=expr.type)

            return Assign(
                name=name,
                expr=expr,
                declared_type=decl_type,
                span=SourceSpan.from_ast(node=node, ctx=ctx.span),
            )

        case ast.Return(value):
            if value is None:
                msg = "return statement must return a value"
                raise TypeError(msg)

            return Return(
                expr=_transform_expr(value, ctx),
                span=SourceSpan.from_ast(node=node, ctx=ctx.span),
            )

        case _:
            msg = f"unsupported statement: {ast.dump(node)}"
            raise TypeError(msg)


def _transform_expr(
    node: ast.expr | None,
    ctx: _AstTransformCtx,
) -> Expr:
    if node is None:
        msg = "return statement must return a non-`None` value."
        raise TypeError(msg)

    span = SourceSpan.from_ast(node=node, ctx=ctx.span)

    match node:
        case ast.Name(id=name):
            if name not in ctx.symbol_table:
                msg = f"unknown variable {name!r}"
                raise TypeError(msg) from None

            return Name(name=name, span=span)

        case ast.Constant(value):
            if isinstance(value, bool) or not isinstance(value, Number):
                msg = f"unsupported constant type `{type(value)}` with value: {value!r}"
                raise TypeError(msg)

            return Constant(
                value=value,
                span=span,
            )

        case ast.BinOp(left=lhs_node, op=ast.Mult(), right=rhs_node):
            lhs = _transform_expr(lhs_node, ctx)
            rhs = _transform_expr(rhs_node, ctx)
            return Binary(
                op=Operator.mul,
                lhs=lhs,
                rhs=rhs,
                span=span,
            )

        case ast.BinOp(left=lhs_node, op=ast.Add(), right=rhs_node):
            lhs = _transform_expr(lhs_node, ctx)
            rhs = _transform_expr(rhs_node, ctx)
            return Binary(
                op=Operator.add,
                lhs=lhs,
                rhs=rhs,
                span=span,
            )

        case _:
            msg = f"unsupported expression: {ast.dump(node)}"
            raise TypeError(msg)


def _transform_annotation(
    annotation: ast.expr,
    ctx: _AstTransformCtx,
) -> QuantityTypeInfo:
    expr = ast.Expression(body=annotation)
    ast.fix_missing_locations(expr)
    value = eval(compile(expr, ctx.span.filename, "eval"), ctx.globals)
    return parse_quantity_annotation(value)


def _parse_quantity_annotation_ast(annotation: ast.expr) -> QuantityTypeInfo:
    match annotation:
        case ast.Subscript(
            value=ast.Name(id="Quantity"),
            slice=ast.Tuple(elts=[element_node, unit_node]),
        ):
            return QuantityTypeInfo(
                element=_parse_element_annotation_ast(element_node),
                unit=_parse_unit_annotation_ast(unit_node),
            )

        case ast.Subscript(
            value=ast.Name(id="Annotated"),
            slice=ast.Tuple(elts=[element_node, unit_node]),
        ):
            return QuantityTypeInfo(
                element=_parse_element_annotation_ast(element_node),
                unit=_parse_unit_annotation_ast(unit_node),
            )

        case _:
            msg = f"unsupported quantity annotation: {ast.dump(annotation)}"
            raise TypeError(msg)


def _parse_element_annotation_ast(node: ast.expr) -> str:
    # TODO(jwh): flesh out the supported value types
    match node:
        case ast.Name(id="float"):
            return "f64"

        case _:
            msg = f"unsupported quantity element type: {ast.dump(node)}"
            raise TypeError(msg)


def _parse_unit_annotation_ast(node: ast.expr) -> Unit:
    match node:
        case ast.Call(
            func=ast.Name(id="Unit"),
            args=[ast.Constant(value=str(expression))],
            keywords=[],
        ):
            return Unit(expression)

        case ast.Constant(value=str(expression)):
            return Unit(expression)

        case _:
            msg = f"unsupported unit annotation: {ast.dump(node)}"
            raise TypeError(msg)
