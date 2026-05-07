from __future__ import annotations

import ast
import inspect
import itertools
import textwrap
from typing import Callable

from units.annotations import Dimensionality, QuantityTypeInfo, UnitInfo
from units.ir import Binary, Expr, Function, Name, Operator, Return
from units.signatures import FunctionSignature


def lower_function(fn: Callable) -> Function:
    signature = FunctionSignature.extract(fn)
    function_def = _get_function_def(fn)

    if len(function_def.body) != 1 or not isinstance(function_def.body[0], ast.Return):
        msg = "only functions with a single return statement are supported"
        raise TypeError(msg)

    environment = {name: type_info for name, type_info in signature.parameters}

    value = _lower_expr(function_def.body[0].value, environment)
    return Function(signature=signature, body=Return(value=value))


def _get_function_def(fn: Callable) -> ast.FunctionDef:
    source = textwrap.dedent(inspect.getsource(fn))
    module = ast.parse(source)

    function_defs = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    if len(function_defs) != 1:
        msg = "expected exactly one function definition"
        raise TypeError(msg)

    return function_defs[0]


def _lower_expr(
    node: ast.expr | None, environment: dict[str, QuantityTypeInfo]
) -> Expr:
    if node is None:
        msg = "return statement must return a non-`None` value."
        raise TypeError(msg)

    match node:
        case ast.Name(id=name):
            if (type_info := environment.get(name)) is None:
                msg = f"unknown variable {name!r}"
                raise TypeError(msg) from None
            return Name(name=name, type=type_info)

        case ast.BinOp(left=lhs_node, op=ast.Mult(), right=rhs_node):
            lhs = _lower_expr(lhs_node, environment)
            rhs = _lower_expr(rhs_node, environment)
            return Binary(
                op=Operator.mul,
                lhs=lhs,
                rhs=rhs,
                type=_mul_type(lhs.type, rhs.type),
            )

        case ast.BinOp(left=lhs_node, op=ast.Add(), right=rhs_node):
            lhs = _lower_expr(lhs_node, environment)
            rhs = _lower_expr(rhs_node, environment)
            return Binary(
                op=Operator.add,
                lhs=lhs,
                rhs=rhs,
                type=_add_type(lhs.type, rhs.type),
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
    while dims and dims[idx] == 0:
        idx -= 1
    return dims[: idx + 1]
