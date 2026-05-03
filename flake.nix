{
  description = "MLIR units demo dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "aarch64-darwin";
    pkgs = import nixpkgs {inherit system;};
    llvm = pkgs.llvmPackages_22;
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = [
        # dev env
        pkgs.git
        pkgs.starship

        # MLIR
        pkgs.cmake
        pkgs.ninja
        pkgs.ccache
        llvm.llvm
        llvm.mlir
        llvm.tblgen

        # testing
        pkgs.python3Packages.lit
        pkgs.gtest

        # frontend
        pkgs.uv
      ];

      shellHook = ''
        export MLIR_DIR="${llvm.mlir.dev}/lib/cmake/mlir"
        export LLVM_DIR="${llvm.llvm.dev}/lib/cmake/llvm"

        export PATH="${llvm.mlir}/bin:${llvm.llvm}/bin:${llvm.clang}/bin:$PATH"

        if [ -n "$BASH_VERSION" ]; then
          eval "$(starship init bash)"
        elif [ -n "$ZSH_VERSION" ]; then
          eval "$(starship init zsh)"
        fi
      '';
    };
  };
}
