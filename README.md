[![Build status](https://badge.buildkite.com/3f339a51886480817a68afdb7c9cef1c49872dad25b8180fa8.svg)](https://buildkite.com/jonathan-helland/smoot-mlir)

> [!warning]
> This is an early-stages proof-of-concept that is not suitable for serious use.

# About

A proof-of-concept JIT compiler for dimensional analysis code in Python. Statically verify the correctness of units calculations without sacrificing on performance.

Units are just a type system for physical calculations. That means that a compiler tailored to that type system can statically analyze the validity of those calculations _and_ strip away any runtime overhead that libraries like [Pint](https://github.com/hgrecco/pint) incur. 

For example, units operations in a hot loop have to repeatedly check for compatibility before doing any conversions:
```python
x = Quantity(1.0, "meter")  # Pint quantity
y = Quantity(1.0, "kilometer")
for _ in range(100):
    x += y  # Must check units compatibility every iteration
```
This is inherently slow and is the key reason why dimensional analysis libraries in Python need to be used judiciously in scientific code.

What if we could do better?

# Usage

You can use the `@compile` decorator to JIT-compile Python functions:
```python
from units import Quantity, Unit, compile

type Meter = Annotated[Quantity, Unit("meter")]
type Second = Annotated[Quantity, Unit("second")]
type MetersPerSecond = Annotated[Quantity, Unit("meter / second")]

@compile
def good(v: MetersPerSecond, dt: Second) -> Meter:
    return v * dt

# Execute optimized native code
good(2.0, 0.5)  # 1.0

# Catch invalid units operations "statically" at import-time.
@compile
def bad(v: MetersPerSecond, dt: Second) -> Meter:
    return v + dt  # <--- ERROR: can't do length + time
```

# Development

## Setup
> [!WARNING]
> This project only supports Apple Silicon, currently.

You need [mise](https://mise.jdx.dev/installing-mise.html) and [nix](https://nixos.org/download/).

Run `mise run shell` to enter a `nix develop` session. This will take some time the first time around to build the environment, including MLIR with Python bindings enabled.

Run `mise run` to see a list of available commands.

# Architecture
The compiler is split into a simple frontend / backend architecture, with the frontend being responsible for translating Python into an IR and the backend handling optimization and lowering into native machine code. 

## Frontend
The frontend uses an AST-based approach, similarly to [Taichi](https://github.com/taichi-dev/taichi). That is, the frontend only supports a subset of the Python language but doesn't need to execute any Python code itself before compilation, unlike tracing JIT compilers like [JAX](https://github.com/jax-ml/jax). Long-term, an bytecode approach like [PyTorch's](https://github.com/pytorch/pytorch) Dynamo would be more robust, but I've opted to keep this prototype simpler.

Python's AST library is used to handle the lexing and parsing phase. Then the AST is transformed into an internal IR model, which is mapped directly into MLIR and passed in-memory to the backend.

## Backend
LLVM's MLIR project is the heart of the backend. We have a custom units dialect that lowers to built-in MLIR dialects and eventually LLVM IR itself. Naturally, LLVM takes care of emitting the machine code.

Note that in the lowering passes, [Smoot](https://github.com/j-helland/smoot) provides the units algebra by way of C++ bindings to its Rust core.

## Build System
Due to the number of moving parts in this repo, I found it prudent to use Nix as the top-level build system. This made it simple to get the right versions of LLVM and MLIR in place in the build environment, which is beyond the ability of [Mise](https://github.com/jdx/mise) to manage well.

[Mise](https://github.com/jdx/mise) is the general task runner, which calls out to other build tools like Cargo (for the Smoot Rust core) and CMake (for the backend). Mise's monorepo tasks are a great fit for a project like this with a handful of distinct packages.

## CI/CD
With Nix already in place, it was also natural to use flake builds and checks for CI pipelines. I dislike second-wave YAML-based CI/CD systems like GitHub Actions, GitLab CI/CD, Buildkite, etc. and will actively try to minimize their presence in my projects when I can get away with it.
