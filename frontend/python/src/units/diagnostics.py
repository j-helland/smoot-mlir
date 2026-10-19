from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

from units.span import SourceSpan


class DiagnosticPhase(Enum):
    frontend = auto()
    emit = auto()
    backend = auto()


@dataclass(frozen=True, slots=True)
class Diagnostic:
    message: str
    phase: DiagnosticPhase
    span: SourceSpan | None = None
    backend_stderr: str | None = None

    @classmethod
    def frontend(
        cls,
        message: str,
        span: SourceSpan | None = None,
    ) -> Diagnostic:
        return cls(
            message=message,
            phase=DiagnosticPhase.frontend,
            span=span,
        )

    @classmethod
    def emit(
        cls,
        message: str,
        span: SourceSpan | None = None,
    ) -> Diagnostic:
        return cls(
            message=message,
            phase=DiagnosticPhase.emit,
            span=span,
        )

    @classmethod
    def backend(
        cls,
        message: str,
        backend_stderr: str | None = None,
        span: SourceSpan | None = None,
    ) -> Diagnostic:
        return cls(
            message=message,
            phase=DiagnosticPhase.backend,
            span=span,
            backend_stderr=backend_stderr,
        )

    def render(self) -> str:
        parts = [self._render_primary()]

        if stderr := self.backend_stderr:
            parts.append("backend stderr:")
            parts.append(stderr.rstrip())

        return "\n".join(parts)

    def _render_primary(self) -> str:
        if self.span is None:
            return self.message

        location = f"{self.span.filename}:{self.span.line}:{self.span.column + 1}"

        source_line = _read_source_line(self.span)
        if source_line is None:
            return f"{location}: {self.message}"

        underline = _render_underline(self.span)

        return "\n".join(
            (
                f"{location}: {self.message}",
                f"\t{source_line.rstrip()}",
                f"\t{underline}",
            )
        )


def _read_source_line(span: SourceSpan) -> str | None:
    # TODO(jwh): consider caching files
    try:
        with open(span.filename) as fd:
            lines = fd.readlines()
    except OSError:
        return None

    if span.line < 1 or span.line > len(lines):
        return None

    return lines[span.line - 1]


def _render_underline(span: SourceSpan) -> str:
    start = max(span.column, 0)
    if span.end_line == span.line and span.end_column is not None:
        end = max(span.end_column, start + 1)
    else:
        end = start + 1

    return " " * start + "^" * max(1, end - start)


DiagnosticLike: TypeAlias = str | Diagnostic


class UnitsCompileError(Exception):
    """Base class for units static analysis errors.

    Defaults to `DiagnosticPhase.frontend` if a plain string message is passed.
    """

    def __init__(self, diagnostic: DiagnosticLike, /):
        if isinstance(diagnostic, str):
            self.diagnostic = Diagnostic.frontend(diagnostic)
        else:
            self.diagnostic = diagnostic
        super().__init__(self.diagnostic.message)

    def __str__(self) -> str:
        return self.diagnostic.render()
