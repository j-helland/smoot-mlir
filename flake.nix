{
  description = "MLIR units demo dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    rust-overlay.url = "github:oxalica/rust-overlay";
    rust-overlay.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {
    self,
    nixpkgs,
    rust-overlay,
  }: let
    system = "aarch64-darwin";
    pkgs = import nixpkgs {
      inherit system;
      overlays = [
        (import rust-overlay)
      ];
    };

    llvm = pkgs.llvmPackages_22;

    rustToolChain = pkgs.rust-bin.stable."1.95.0".default.override {
      extensions = [
        "rust-src"
        "rustfmt"
        "clippy"
      ];
    };

  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = [
        # dev env
        pkgs.git
        pkgs.fish
        pkgs.mise
        pkgs.starship
        pkgs.usage

        # Rust core
        rustToolChain

        # MLIR
        pkgs.cmake
        pkgs.ninja
        pkgs.ccache
        llvm.llvm
        llvm.clang-tools
        llvm.mlir
        llvm.tblgen

        # testing
        pkgs.python3Packages.lit
        pkgs.gtest

        # frontend
        pkgs.uv
      ];

      shellHook = ''
        export LLVM_DIR="${llvm.llvm.dev}/lib/cmake/llvm"
        export MLIR_DIR="${llvm.mlir.dev}/lib/cmake/mlir"
        export MLIR_TABLEGEN_EXE="${llvm.tblgen}/bin/mlir-tblgen"
      '';
    };
  };
}
