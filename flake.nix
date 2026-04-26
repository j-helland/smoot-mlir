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
        pkgs.cmake
        pkgs.ninja
        pkgs.ccache
        llvm.llvm
        llvm.mlir
        llvm.clang
      ];

      shellHook = ''
        export MLIR_DIR="${llvm.mlir}/lib/cmake/mlir"
        export LLVM_DIR="${llvm.llvm.dev}/lib/cmake/llvm"

        export PATH="${llvm.mlir}/bin:${llvm.llvm}/bin:${llvm.clang}/bin:$PATH"
      '';
    };
  };
}
