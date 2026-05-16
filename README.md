# Setup

> [!WARNING]
> This project only supports Apple Silicon, currently.

You need [mise](https://mise.jdx.dev/installing-mise.html).

## Apple Silicon
Clone and build LLVM with MLIR support.
Make sure that MLIR supports plugins via dynamic linking.
```shell
git clone https://github.com/llvm/llvm-project.git
mkdir llvm-project/build-arm64
cd llvm-project/build-arm64

# configure
cmake -G Ninja ../llvm \
    -DLLVM_ENABLE_PROJECTS=mlir \
    -DLLVM_BUILD_EXAMPLES=ON \
    -DLLVM_TARGETS_TO_BUILD=host \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_ENABLE_ASSERTIONS=ON \
    -DCMAKE_C_COMPILER=/usr/bin/clang \
    -DCMAKE_CXX_COMPILER=/usr/bin/clang++ \
    -DLLVM_CCACHE_BUILD=ON \
    -DLLVM_ENABLE_PLUGINS=ON \
    -DLLVM_BUILD_LLVM_DYLIB=ON \
    -DMLIR_LINK_MLIR_DYLIB=ON \
    -DBUILD_SHARED_LIBS=OFF

# build
ninja

# install
# (fish shell)
fish_add_path $(pwd)/bin
```

# Usage
```shell
mise run 
```

# C++ Tooling

The repository uses LLVM-style formatting and compile-database-backed linting for
the MLIR/C++ code.

```shell
# Format C++ and TableGen files.
mise run format-cpp

# Check formatting without modifying files.
mise run format-cpp-check

# Run clang-tidy using build-arm64/compile_commands.json.
mise run tidy-cpp

# Run the full C++ lint stack.
mise run lint

# Run backend tests with AddressSanitizer and UndefinedBehaviorSanitizer.
mise run test-backend-sanitizers
```

`tidy-cpp` depends on `build-backend`, which configures CMake with
`CMAKE_EXPORT_COMPILE_COMMANDS=ON`.

You can also opt into build-integrated checks when configuring CMake manually:

```shell
cmake -S . -B build-arm64 \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DUNITS_ENABLE_CLANG_TIDY=ON \
  -DUNITS_ENABLE_ASAN=ON \
  -DUNITS_ENABLE_UBSAN=ON
```
