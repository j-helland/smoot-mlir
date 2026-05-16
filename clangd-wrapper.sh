#!/bin/bash

# NOTE(jwh): Editors like VSCode and Zed need to run clangd from within the nix dev environment
#            so that nix-provided LLVM can be used. Otherwise, we get a bunch of LSP errors.
exec nix develop --command clangd \
    --query-driver='/nix/store/*clang*/bin/clang++,/nix/store/*clang-wrapper*/bin/clang++'
