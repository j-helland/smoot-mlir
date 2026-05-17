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
    lib = nixpkgs.lib;
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

    backendEnv = {
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
      UV_PYTHON = "${pkgs.python314}/bin/python3";
      UV_PYTHON_DOWNLOADS = "never";
    };

    exportBackendEnv = lib.concatStringsSep "\n" (
      lib.mapAttrsToList (name: value: "export ${name}=\"${value}\"") backendEnv
    );

    backendNativeBuildInputs = [
      pkgs.cmake
      pkgs.ninja
      pkgs.mise
      pkgs.uv
      pkgs.python314
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

  in {
    #==================================================
    # Backend tests
    #==================================================
    checks.${system}.backend = llvm.stdenv.mkDerivation {
      pname = "units-backend-check";
      version = "0.0.0";
      src = self;

      nativeBuildInputs = backendNativeBuildInputs;
      buildInputs = backendBuildInputs;

      doCheck = true;
      dontConfigure = true;

      buildPhase = ''
        runHook preBuild

        ${exportBackendEnv}
        export CARGO_HOME="$TMPDIR/cargo-home"
        export MISE_CACHE_DIR="$TMPDIR/mise-cache"
        export MISE_CONFIG_DIR="$TMPDIR/mise-config"
        export MISE_DATA_DIR="$TMPDIR/mise-data"
        export MISE_STATE_DIR="$TMPDIR/mise-state"
        export UV_CACHE_DIR="$TMPDIR/uv-cache"

        mise trust --all --yes
        mise run --skip-tools test-backend
        mise run --skip-tools test-backend-sanitizers

        runHook postBuild
      '';

      checkPhase = ''
        runHook preCheck
        runHook postCheck
      '';

      installPhase = ''
        mkdir -p "$out"
        touch "$out/backend-check-passed"
      '';
    };

    #==================================================
    # Dev shell
    #==================================================
    devShells.${system}.default = pkgs.mkShell {
      packages =
        [
          # dev env
          pkgs.git
          pkgs.fish
          pkgs.starship
          pkgs.usage

          pkgs.ccache
        ]
        ++ backendNativeBuildInputs
        ++ backendBuildInputs;

      shellHook = ''
        ${exportBackendEnv}

        export PATH="${llvm.clang-tools}/bin:${llvm.mlir}/bin:${llvm.llvm}/bin:$PATH"

        # Make sure that Python from any nix managed tools can't interfere with
        # the rest of the project, which uses uv to manage Python.
        unset PYTHONPATH
      '';
    };
  };
}
