from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum, auto
from numbers import Number
from typing import TypeVar

from typing_extensions import dataclass_transform

from units.annotations import QuantityTypeInfo
from units.signatures import FunctionSignature

T = TypeVar("T")


@dataclass_transform(frozen_default=True, kw_only_default=True)
def ir_model(t: type[T]) -> type[T]:
    return dataclass(
        frozen=True,
        slots=True,
        kw_only=True,
    )(t)


@ir_model
class SourceSpan:
    filename: str
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None

    @dataclass(frozen=True, slots=True)
    class Ctx:
        filename: str
        lineno_offset: int = 0

    @classmethod
    def from_ast(
        cls,
        node: ast.AST,
        ctx: Ctx,
    ) -> SourceSpan:
        """Build the code span from a Python AST node."""
        line = getattr(node, "lineno", 0) + ctx.lineno_offset
        end_line = getattr(node, "end_lineno", None)
        if end_line is not None:
            end_line += ctx.lineno_offset

        return cls(
            filename=ctx.filename,
            line=line,
            column=getattr(node, "col_offset", 0),
            end_line=end_line,
            end_column=getattr(node, "end_col_offset", None),
        )


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
