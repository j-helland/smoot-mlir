from __future__ import annotations

import ast
import inspect
import itertools
import textwrap
from dataclasses import dataclass
from types import FunctionType
from typing import Callable, Final, TypeAlias

from units.annotations import Dimensionality, QuantityTypeInfo, UnitInfo
from units.ir import (
    Binary,
    Expr,
    Function,
    Name,
    Operator,
    Return,
    SourceSpan,
    Stmt,
)
from units.signatures import FunctionSignature

EnvironmentType: TypeAlias = dict[str, QuantityTypeInfo]

UNKNOWN_SOURCE_FILE: Final[str] = "<unknown>"


def lower_function(fn: FunctionType) -> Function:
    signature = FunctionSignature.extract(fn)
    function_def = _get_function_def(fn)
    filename = inspect.getsourcefile(fn) or UNKNOWN_SOURCE_FILE
    _, start_line = inspect.getsourcelines(fn)
    lineno_offset = start_line - 1  # inspect returns 1-based

    if len(function_def.body) != 1 or not isinstance(function_def.body[0], ast.Return):
        msg = "only functions with a single return statement are supported"
        raise TypeError(msg)

    environment = {name: type_info for name, type_info in signature.parameters}
    span_ctx = SourceSpan.Ctx(filename=filename, lineno_offset=lineno_offset)
    ctx = _LowerCtx(environment=environment, span=span_ctx)

    body = _lower_body(function_def, ctx)
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


@dataclass(frozen=True, slots=True)
class _LowerCtx:
    environment: EnvironmentType
    span: SourceSpan.Ctx


def _lower_body(
    function_def: ast.FunctionDef,
    ctx: _LowerCtx,
) -> tuple[Stmt, ...]:
    if not function_def.body:
        msg = "function body must not be empty"
        raise TypeError(msg)

    statements = tuple(_lower_stmt(stmt, ctx) for stmt in function_def.body)

    if not any(isinstance(statement, Return) for statement in statements):
        msg = "function must contain a return statement"
        raise TypeError(msg)

    return statements


def _lower_stmt(
    node: ast.stmt,
    ctx: _LowerCtx,
) -> Stmt:
    match node:
        case ast.Return(value=value_node):
            if value_node is None:
                msg = "return statement must return a value"
                raise TypeError(msg)

            return Return(
                expr=_lower_expr(value_node, ctx),
                span=SourceSpan.from_ast(node=node, ctx=ctx.span),
            )

        case _:
            msg = f"unsupported statement: {ast.dump(node)}"
            raise TypeError(msg)


def _lower_expr(
    node: ast.expr | None,
    ctx: _LowerCtx,
) -> Expr:
    if node is None:
        msg = "return statement must return a non-`None` value."
        raise TypeError(msg)

    span = SourceSpan.from_ast(node=node, ctx=ctx.span)

    match node:
        case ast.Name(id=name):
            if (type_info := ctx.environment.get(name)) is None:
                msg = f"unknown variable {name!r}"
                raise TypeError(msg) from None
            return Name(name=name, type=type_info, span=span)

        case ast.BinOp(left=lhs_node, op=ast.Mult(), right=rhs_node):
            lhs = _lower_expr(lhs_node, ctx)
            rhs = _lower_expr(rhs_node, ctx)
            return Binary(
                op=Operator.mul,
                lhs=lhs,
                rhs=rhs,
                type=_mul_type(lhs.type, rhs.type),
                span=span,
            )

        case ast.BinOp(left=lhs_node, op=ast.Add(), right=rhs_node):
            lhs = _lower_expr(lhs_node, ctx)
            rhs = _lower_expr(rhs_node, ctx)
            return Binary(
                op=Operator.add,
                lhs=lhs,
                rhs=rhs,
                type=_add_type(lhs.type, rhs.type),
                span=span,
            )

        case _:
            msg = f"unsupported expression: {ast.dump(node)}"
            raise TypeError(msg)


def _mul_type(lhs: QuantityTypeInfo, rhs: QuantityTypeInfo) -> QuantityTypeInfo:
    return QuantityTypeInfo(
        element=_combine_element_types(lhs, rhs),
        unit=UnitInfo(dims=_add_dims(lhs.unit.dims, rhs.unit.dims)),
    )


def _combine_element_types(lhs: QuantityTypeInfo, rhs: QuantityTypeInfo) -> str:
    if lhs.element != rhs.element:
        msg = f"Mixed element types are not supported. lhs={lhs.element} rhs={rhs.element}"
        raise TypeError(msg)
    return lhs.element


def _add_type(lhs: QuantityTypeInfo, _rhs: QuantityTypeInfo) -> QuantityTypeInfo:
    return lhs


def _add_dims(lhs: Dimensionality, rhs: Dimensionality) -> Dimensionality:
    dims = tuple((ld + rd for ld, rd in itertools.zip_longest(lhs, rhs, fillvalue=0)))
    return _canonicalize_dims(dims)


def _canonicalize_dims(dims: Dimensionality) -> Dimensionality:
    # Drop trailing zero dimensions
    idx = len(dims) - 1
    while idx >= 0 and dims[idx] == 0:
        idx -= 1
    return dims[: idx + 1]
