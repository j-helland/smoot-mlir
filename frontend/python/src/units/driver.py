from __future__ import annotations

import functools
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich import print

from units import UnitsCompileError


def _parse_command_exists(value: str | Path) -> str:
    if (command := shutil.which(value)) is None:
        msg = f"No such command '{value}'"
        raise UnitsCompileError from ValueError(msg)
    return command


CommandExistsField = Annotated[str, BeforeValidator(_parse_command_exists)]
"""Pydantic field type that validates that a file exists."""


class UnitsOpt(BaseSettings):
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

    def run_units_opt(self, input: str) -> str:
        """Run units-mlir opt passes and return the emitted IR."""
        cmd = (self.units_opt,)
        result = subprocess.run(
            cmd,
            input=input,
            text=True,
            capture_output=True,
        )
        try:
            result.check_returncode()
        except subprocess.CalledProcessError as e:
            print(f"[dim italic]--- STDERR: {self.units_opt} ---[/dim italic]")
            print(result.stderr)

            msg = "compiler backend units-opt failed"
            raise UnitsCompileError(msg) from e
        result.check_returncode()

        return result.stdout
