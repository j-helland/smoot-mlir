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
        pkgs.fish
        pkgs.mise
        pkgs.starship
        pkgs.usage

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
        export MLIR_DIR="${llvm.mlir.dev}/lib/cmake/mlir"
        export LLVM_DIR="${llvm.llvm.dev}/lib/cmake/llvm"

        export PATH="${llvm.mlir}/bin:${llvm.llvm}/bin:${llvm.clang}/bin:$PATH"

        if [ -z "$IN_NIX_FISH" ] && [ -t 1 ]; then
          export IN_NIX_FISH=1
          exec fish -C 'starship init fish | source; mise completion fish | source'
        fi
      '';
    };
  };
}
