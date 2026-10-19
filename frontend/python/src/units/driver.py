from __future__ import annotations

import functools
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich import print

from units import _units_backend
from units.diagnostics import Diagnostic, UnitsCompileError
from units.mlir_emit import GeneratedModule


class NativeBackend:
    __slots__ = ()

    @classmethod
    @functools.lru_cache(maxsize=1)
    def default(cls) -> NativeBackend:
        return cls()

    def verify_mlir(self, input: GeneratedModule | str) -> None:
        text = input.text if isinstance(input, GeneratedModule) else input
        try:
            _units_backend.verify_mlir(text)
        except _units_backend.BackendError as e:
            raise UnitsCompileError(Diagnostic.backend(message=str(e))) from e

    def compile_mlir(
        self,
        input: GeneratedModule | str,
        entrypoint: str,
    ) -> Callable[[float], float]:
        text = input.text if isinstance(input, GeneratedModule) else input
        try:
            return _units_backend.compile_mlir(text, entrypoint)
        except _units_backend.BackendError as e:
            raise UnitsCompileError(Diagnostic.backend(message=str(e))) from e


def _parse_command_exists(value: str | Path) -> str:
    if (command := shutil.which(value)) is None:
        msg = f"No such command '{value}'"
        raise UnitsCompileError(msg)
    return command


CommandExistsField = Annotated[str, BeforeValidator(_parse_command_exists)]
"""Pydantic field type that validates that a file exists."""


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
