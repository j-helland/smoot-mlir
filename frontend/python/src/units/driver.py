from __future__ import annotations

import functools
import shutil
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from mlir import ir
from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich import print

from units import _units_backend
from units.diagnostics import Diagnostic, UnitsCompileError
from units.span import SourceSpan


@dataclass(slots=True)
class NativeBackend:
    @classmethod
    @functools.lru_cache(maxsize=1)
    def default(cls) -> NativeBackend:
        return cls()

    def verify_mlir(self, module: ir.Module) -> None:
        try:
            module.operation.verify()
        except ir.MLIRError as e:  # ty: ignore[unresolved-attribute] MLIR dynamically adds the error type
            raise UnitsCompileError(Diagnostic.backend(message=str(e))) from e

    def compile_mlir(
        self,
        module: ir.Module,
        entrypoint: str,
    ) -> _units_backend.CompiledFunction:
        try:
            return _units_backend.compile_mlir(module, entrypoint)
        except _units_backend.BackendError as e:
            raise UnitsCompileError(Diagnostic.backend(message=str(e))) from e


def _parse_command_exists(value: str | Path) -> str:
    if (command := shutil.which(value)) is None:
        msg = f"No such command '{value}'"
        raise UnitsCompileError(msg)
    return command


CommandExistsField = Annotated[str, BeforeValidator(_parse_command_exists)]
"""Pydantic field type that validates that a file exists."""


@dataclass(frozen=True, slots=True)
class GeneratedModule:
    text: str
    line_map: Mapping[int, SourceSpan]


class UnitsOpt(BaseSettings):
    """Wrapper around the units-opt commandline tool.

    Useful for testing the compiler frontend's MLIR emission because it uses a textual
    representation for the IR.
    """

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
    )

    units_opt: CommandExistsField = "units-opt"
    """Reads from UNITS_OPT env var."""

    # NOTE(jwh): class-level caching does _not_ have the memory-leak problems of instance-level caching.
    @classmethod
    @functools.lru_cache(maxsize=1)
    def default(cls) -> UnitsOpt:
        return cls()

    def run_units_opt(self, input: GeneratedModule | str) -> str:
        """Run units-mlir opt passes and return the emitted IR."""
        if isinstance(input, GeneratedModule):
            text = input.text
        else:
            text = input

        cmd = (self.units_opt,)
        result = subprocess.run(
            cmd,
            check=False,
            input=text,
            text=True,
            capture_output=True,
        )
        try:
            result.check_returncode()
        except subprocess.CalledProcessError as e:
            print(f"[dim italic]--- STDERR: {self.units_opt} ---[/dim italic]")
            print(result.stderr)

            raise UnitsCompileError(
                Diagnostic.backend(
                    message="compiler backend units-opt failed",
                    backend_stderr=result.stderr,
                )
            ) from e
        result.check_returncode()

        return result.stdout
