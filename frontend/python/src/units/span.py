from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
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
        column_offset: int = 0

        def to_span(self) -> SourceSpan:
            return SourceSpan(
                filename=self.filename,
                line=self.lineno_offset,
                column=0,
            )

    @classmethod
    def from_ast(
        cls,
        node: ast.AST,
        ctx: Ctx,
    ) -> SourceSpan:
        """Build the code span from a Python AST node."""
        line = getattr(node, "lineno", 0) + ctx.lineno_offset

        column = getattr(node, "col_offset", 0) + ctx.column_offset
        end_column = getattr(node, "end_col_offset", None)
        if end_column is not None:
            end_column += ctx.column_offset

        end_line = getattr(node, "end_lineno", None)
        if end_line is not None:
            end_line += ctx.lineno_offset

        return cls(
            filename=ctx.filename,
            line=line,
            column=column,
            end_line=end_line,
            end_column=end_column,
        )
