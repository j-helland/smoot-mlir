from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from units.annotations import QuantityTypeInfo
from units.signatures import FunctionSignature


class Expr:
    type: QuantityTypeInfo


@dataclass(frozen=True)
class Name(Expr):
    name: str
    type: QuantityTypeInfo


class Operator(Enum):
    add = auto()
    mul = auto()


@dataclass(frozen=True)
class Binary(Expr):
    op: Operator
    lhs: Expr
    rhs: Expr
    type: QuantityTypeInfo


@dataclass(frozen=True)
class Return:
    value: Expr


@dataclass(frozen=True)
class Function:
    signature: FunctionSignature
    body: Return
