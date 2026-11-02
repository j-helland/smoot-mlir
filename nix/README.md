# Nix configuration

The files here are ordinary Nix functions with explicit arguments. They are called by the root [flake.nix](../flake.nix).

- `default.nix` composes the packages, checks, and development shell for one system.
- `mlir.nix` customizes MLIR, including Python bindings and Darwin library fixes.
- `python.nix` creates the uv2nix environments and MLIR Python runtime dependencies.
- `toolchain.nix` selects Rust and defines shared build dependencies and tool paths.
- `backend.nix` builds, tests, and installs the backend with vendored Cargo dependencies.
- `checks.nix` defines the frontend and lint checks and reuses the backend package.
- `shell.nix` exposes the toolchain and MLIR Python bindings for development.

To add a native platform, extend `systems` in [flake.nix](../flake.nix).

CI is configured in [`.buildkite/pipeline.yml`](../.buildkite/pipeline.yml).
