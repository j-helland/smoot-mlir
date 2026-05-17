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
            phase=DiagnosticPhase.emit,
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
            phase=DiagnosticPhase.emit,
            span=span,
            backend_stderr=backend_stderr,
        )


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
