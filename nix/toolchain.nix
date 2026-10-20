{
  pkgs,
  llvm,
  devtoolsPythonEnv,
  uvEnv,
}:
let
  lib = pkgs.lib;
  rustToolChain = pkgs.rust-bin.stable."1.95.0".default.override {
    extensions = [
      "rust-src"
      "rustfmt"
      "clippy"
    ];
  };

  backendEnv = uvEnv // {
    CC = "${llvm.clang}/bin/clang";
    CXX = "${llvm.clang}/bin/clang++";
    AR = "${llvm.llvm}/bin/llvm-ar";
    RANLIB = "${llvm.llvm}/bin/llvm-ranlib";
    NM = "${llvm.llvm}/bin/llvm-nm";
    LLVM_DIR = "${llvm.llvm.dev}/lib/cmake/llvm";
    MLIR_DIR = "${llvm.mlir.dev}/lib/cmake/mlir";
    MLIR_TABLEGEN_EXE = "${llvm.tblgen}/bin/mlir-tblgen";
    CLANG_FORMAT_EXE = "${llvm.clang-tools}/bin/clang-format";
    CLANG_TIDY_EXE = "${llvm.clang-tools}/bin/clang-tidy";
  };

  exportEnv =
    env:
    lib.concatStringsSep "\n" (lib.mapAttrsToList (name: value: "export ${name}=\"${value}\"") env);

  exportBackendEnv = exportEnv backendEnv;
  exportUvEnv = exportEnv uvEnv;

  backendNativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
    pkgs.git
    pkgs.mise
    pkgs.uv
    pkgs.rust-cbindgen
    devtoolsPythonEnv
    rustToolChain
    llvm.llvm
    llvm.clang
    llvm.clang-tools
    llvm.bintools
    llvm.mlir
    llvm.tblgen
  ];

  backendBuildInputs = [
    pkgs.gtest
    llvm.llvm
    llvm.mlir
  ];
in
{
  inherit
    backendNativeBuildInputs
    backendBuildInputs
    exportBackendEnv
    exportUvEnv
    ;
}
