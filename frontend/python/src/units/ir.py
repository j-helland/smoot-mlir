from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from numbers import Number
from typing import TypeVar, dataclass_transform

from units.annotations import QuantityTypeInfo
from units.signatures import FunctionSignature
from units.span import SourceSpan

T = TypeVar("T")


@dataclass_transform(frozen_default=True, kw_only_default=True)
def ir_model[T](t: type[T]) -> type[T]:
    return dataclass(
        frozen=True,
        slots=True,
        kw_only=True,
    )(t)


@ir_model
class Node:
    span: SourceSpan | None = None


@ir_model
class Stmt(Node):
    pass


@ir_model
class Expr(Node):
    type: QuantityTypeInfo | None = None


@ir_model
class Name(Expr):
    name: str


class Operator(Enum):
    add = auto()
    mul = auto()


@ir_model
class Binary(Expr):
    op: Operator
    lhs: Expr
    rhs: Expr


@ir_model
class Return(Stmt):
    expr: Expr


@ir_model
class Function(Stmt):
    signature: FunctionSignature
    body: tuple[Stmt, ...]


@ir_model
class Constant(Expr):
    value: Number


@ir_model
class Assign(Stmt):
    name: str
    expr: Expr
    declared_type: QuantityTypeInfo | None = None
