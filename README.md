[![Build status](https://badge.buildkite.com/3f339a51886480817a68afdb7c9cef1c49872dad25b8180fa8.svg)](https://buildkite.com/jonathan-helland/smoot-mlir)

# Usage

TODO(jwh)

# Development

## Setup
> [!WARNING]
> This project only supports Apple Silicon, currently.

You need [mise](https://mise.jdx.dev/installing-mise.html) and [nix](https://nixos.org/download/).

Run `mise run shell` to enter a `nix develop` session. This will take some time the first time around to build the environment, including MLIR with Python bindings enabled.

Run `mise run` to see a list of available commands.

## C++ Tooling
The sanitizer tests disable ASan container overflow checks because the
prebuilt MLIR library is not ASan-instrumented. STL containers shared between
the two builds can otherwise produce false positives during pattern registration.

Sanitizer builds keep the Python extension in `build-sanitizers/bindings/python`
so they do not overwrite the regular extension used by frontend tests. Loading an
ASan-instrumented extension into regular Python can abort during import on macOS.

`tidy-cpp` depends on `build-backend`, which configures CMake with
`CMAKE_EXPORT_COMPILE_COMMANDS=ON`.

You can also opt into build-integrated checks when configuring CMake manually:

```shell
cmake -S . -B build \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DUNITS_ENABLE_CLANG_TIDY=ON \
  -DUNITS_ENABLE_ASAN=ON \
  -DUNITS_ENABLE_UBSAN=ON
```

# Architecture

TODO(jwh)

# TODOs

- [ ] Build system to package MLIR runtime and bindings with the wheel. Probably scikit-build-core.
