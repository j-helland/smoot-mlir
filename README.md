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

