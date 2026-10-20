[![NixCI](https://nix-ci.com/badge/gh:j-helland:smoot-mlir)](https://nix-ci.com/gh:j-helland:smoot-mlir)

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
