from __future__ import annotations

import ast
import dataclasses
import inspect
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from types import FunctionType
from typing import Final

from units.annotations import QuantityTypeInfo, parse_quantity_annotation
from units.diagnostics import Diagnostic, UnitsCompileError
from units.ir import (
    Assign,
    Binary,
    Constant,
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
from units.quantity import Unit
from units.signatures import FunctionSignature
from units.span import SourceSpan


@dataclass(frozen=True, kw_only=True)
class Symbol:
    type: QuantityTypeInfo | None = None


type SymbolTableType = dict[str, Symbol]

UNKNOWN_SOURCE_FILE: Final[str] = "<unknown>"


def transform_ast(value: object) -> Node:
    match value:
        case FunctionType():
            return _transform_function(value)
        case _:
            raise UnitsCompileError from NotImplementedError(type(value))


def _transform_function(fn: FunctionType) -> Function:
    signature = FunctionSignature.extract(fn)
    parsed = _get_function_def(fn)

    symbol_table = {
        name: Symbol(
            type=decl_type,
        )
        for name, decl_type in signature.parameters
    }
    ctx = _AstTransformCtx(
        symbol_table=symbol_table,
        span=parsed.span_ctx,
        globals=fn.__globals__,
    )

    body = _transform_body(parsed.function_def, ctx)
    return Function(
        signature=signature,
        body=body,
        span=SourceSpan.from_ast(parsed.function_def, parsed.span_ctx),
    )


@dataclass(frozen=True, slots=True)
class _ParsedFunction:
    function_def: ast.FunctionDef
    span_ctx: SourceSpan.Ctx


def _get_function_def(fn: Callable) -> _ParsedFunction:
    filename = inspect.getsourcefile(fn) or UNKNOWN_SOURCE_FILE
    source_lines, start_line = inspect.getsourcelines(fn)

    source = "".join(source_lines)
    dedented = textwrap.dedent(source)
    module = ast.parse(dedented)

    function_defs = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if len(function_defs) != 1:
        msg = "expected exactly one function definition"
        raise UnitsCompileError(msg)

    # Inspect is 1-indexed
    # AST lines are relative to the dedent
    lineno_offset = start_line - 1

    # How much dedent removed from the whole snippet
    column_offset = len(source_lines[0]) - len(source_lines[0].lstrip())

    return _ParsedFunction(
        function_def=function_defs[0],
        span_ctx=SourceSpan.Ctx(
            filename=filename,
            lineno_offset=lineno_offset,
            column_offset=column_offset,
        ),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class _AstTransformCtx:
    symbol_table: SymbolTableType
    span: SourceSpan.Ctx
    globals: dict[str, object]
    is_in_loop: bool = False


def _transform_body(
    function_def: ast.FunctionDef,
    ctx: _AstTransformCtx,
) -> tuple[Stmt, ...]:
    statements = tuple(_transform_stmt(stmt, ctx) for stmt in function_def.body)

    if not any(isinstance(statement, Return) for statement in statements):
        msg = "function must contain a return statement"
        span = SourceSpan.from_ast(function_def, ctx.span)
        raise UnitsCompileError(Diagnostic.frontend(msg, span))

    return statements


def _transform_stmt(
    node: ast.stmt,
    ctx: _AstTransformCtx,
) -> Stmt:
    span = SourceSpan.from_ast(node, ctx.span)

    match node:
        case ast.Assign([ast.Name(id=name)], value, _):
            expr = _transform_expr(value, ctx)
            ctx.symbol_table[name] = Symbol(type=expr.type)
            return Assign(name=name, expr=expr, span=span)

        case ast.AnnAssign(ast.Name(id=name), annotation, value, simple):
            if simple != 1:
                msg = "only simple annotated assignments are supported"
                raise UnitsCompileError(Diagnostic.frontend(msg, span))

            if value is None:
                msg = "annotated assignments must include a value"
                raise UnitsCompileError(Diagnostic.frontend(msg, span))

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
                raise UnitsCompileError(Diagnostic.frontend(msg, span))

            if ctx.is_in_loop:
                msg = "return inside a loop is not supported yet"
                raise UnitsCompileError(Diagnostic.frontend(msg, span))

            return Return(
                expr=_transform_expr(value, ctx),
                span=SourceSpan.from_ast(node=node, ctx=ctx.span),
            )

        case ast.For() as loop:
            return _transform_for_loop(loop, node, ctx, span)

        case _:
            msg = f"unsupported statement: {ast.dump(node)}"
            raise UnitsCompileError(Diagnostic.frontend(msg, span))


def _transform_for_loop(
    loop: ast.For,
    node: ast.stmt,
    ctx: _AstTransformCtx,
    span: SourceSpan,
) -> For:
    if loop.orelse:
        msg = "for loop else statements are unsupported"
        raise UnitsCompileError(Diagnostic.frontend(msg, span))

    if not isinstance(loop.target, ast.Name) or loop.target.id != "_":
        msg = "only an ignored loop target '_' is supported"
        raise UnitsCompileError(Diagnostic.frontend(msg, span))

    iterable = _transform_expr(loop.iter, ctx)
    loop_ctx = dataclasses.replace(
        ctx,
        # copy to avoid making in-loop symbols available out of loop context
        symbol_table=ctx.symbol_table.copy(),
        is_in_loop=True,
    )
    statements = (_transform_stmt(stmt, loop_ctx) for stmt in loop.body)

    return For(
        target=loop.target.id,
        iterable=iterable,
        body=tuple(statements),
        span=span,
    )


def _transform_expr(
    node: ast.expr | None,
    ctx: _AstTransformCtx,
) -> Expr:
    if node is None:
        msg = "return statement must return a non-`None` value."
        raise UnitsCompileError(
            Diagnostic.frontend(
                message=msg,
                span=ctx.span.to_span(),
            )
        )

    span = SourceSpan.from_ast(node, ctx.span)

    match node:
        case ast.Name(id=name):
            if name not in ctx.symbol_table:
                msg = f"unknown variable {name!r}"
                raise UnitsCompileError(Diagnostic.frontend(msg, span))

            return Name(name=name, span=span)

        case ast.Constant(value):
            if isinstance(value, bool) or not isinstance(value, int | float):
                msg = f"unsupported constant type `{type(value)}` with value: {value!r}"
                raise UnitsCompileError(Diagnostic.frontend(msg, span))

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

        case ast.Call(func=ast.Name(id="range")) as call:
            return _transform_range(call, ctx)

        case _:
            msg = f"unsupported expression: {ast.dump(node)}"
            raise UnitsCompileError(Diagnostic.frontend(msg, span))


def _transform_range(
    call: ast.Call,
    ctx: _AstTransformCtx,
) -> Range:
    span = SourceSpan.from_ast(call, ctx.span)
    match call:
        case ast.Call(
            args=[ast.Constant(value=stop) as bound],
            keywords=[],
        ) if type(stop) is int and stop >= 0:
            return Range(
                start=Constant(value=0, span=span),
                stop=_transform_expr(bound, ctx),
                step=Constant(value=1, span=span),
                span=span,
            )

        # TODO(jwh): support more than just `for _ in range(N)`
        case _:
            msg = "expected range(N) with nonnegative integer literal"
            raise UnitsCompileError(Diagnostic.frontend(msg, span))


def _transform_annotation(
    annotation: ast.expr,
    ctx: _AstTransformCtx,
) -> QuantityTypeInfo:
    match annotation:
        case ast.Name(id=name) if name in ctx.globals:
            return parse_quantity_annotation(
                ctx.globals[name],
                span=SourceSpan.from_ast(annotation, ctx.span),
            )

        case ast.Subscript(
            value=ast.Name(id="Annotated"),
            slice=ast.Tuple(elts=[element_node, unit_node]),
        ):
            return QuantityTypeInfo(
                element=_parse_element_annotation_ast(element_node, ctx),
                unit=_parse_unit_annotation_ast(unit_node, ctx),
            )

        case _:
            msg = f"unsupported quantity annotation: {ast.dump(annotation)}"
            span = SourceSpan.from_ast(annotation, ctx.span)
            raise UnitsCompileError(Diagnostic.frontend(msg, span))


def _parse_element_annotation_ast(
    node: ast.expr,
    ctx: _AstTransformCtx,
) -> str:
    match node:
        case ast.Name("float"):
            return "f64"

        case ast.Subscript(value=ast.Name(id="Quantity"), slice=backing):
            return _parse_element_annotation_ast(backing, ctx)

        case _:
            msg = f"unsupported quantity element type: {ast.dump(node)}"
            span = SourceSpan.from_ast(node, ctx.span)
            raise UnitsCompileError(Diagnostic.frontend(msg, span))


def _parse_unit_annotation_ast(
    node: ast.expr,
    ctx: _AstTransformCtx,
) -> Unit:
    match node:
        case ast.Name(id=name) if isinstance(ctx.globals.get(name), (Unit, str)):
            unit = ctx.globals[name]
            return unit if isinstance(unit, Unit) else Unit(str(unit))

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
            span = SourceSpan.from_ast(node, ctx.span)
            raise UnitsCompileError(Diagnostic.frontend(msg, span))
