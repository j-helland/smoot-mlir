{
  description = "MLIR units demo dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    rust-overlay.url = "github:oxalica/rust-overlay";
    rust-overlay.inputs.nixpkgs.follows = "nixpkgs";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      rust-overlay,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
    }:
    let
      lib = nixpkgs.lib;
      systems = [
        "aarch64-darwin"
        "x86_64-linux"
      ];

      forAllSystems = lib.genAttrs systems;

      mkSystemOutputs =
        system:
        let
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

          workspace = uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };

          uvOverlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };

          python = pkgs.python314;

          pythonBase = pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          };

          pythonSet = pythonBase.overrideScope (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.wheel
              uvOverlay
            ]
          );

          devtoolsPythonEnv = pythonSet.mkVirtualEnv "units-devtools-env" {
            devtools = [ "dev" ];
          };

          frontendPythonEnv = pythonSet.mkVirtualEnv "units-frontend-test-env" {
            units = [ "dev" ];
          };

          uvEnv = {
            UV_PYTHON = "${python}/bin/python3";
            UV_PYTHON_DOWNLOADS = "never";
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

          exportPythonToolEnv = ''
            export PYTHON_EXE="${devtoolsPythonEnv}/bin/python3"
            export PYBIND11_DIR="$("$PYTHON_EXE" -m pybind11 --cmakedir)"
            export LIT_EXE="${devtoolsPythonEnv}/bin/lit"
          '';

          backendPackage = llvm.stdenv.mkDerivation {
            pname = "units-backend";
            version = "0.0.0";
            src = self;

            nativeBuildInputs = backendNativeBuildInputs;
            buildInputs = backendBuildInputs;

            doCheck = true;
            dontConfigure = true;

            buildPhase = ''
              runHook preBuild

              ${exportBackendEnv}
              ${exportPythonToolEnv}
              export CARGO_HOME="$TMPDIR/cargo-home"
              export MISE_CACHE_DIR="$TMPDIR/mise-cache"
              export MISE_CONFIG_DIR="$TMPDIR/mise-config"
              export MISE_DATA_DIR="$TMPDIR/mise-data"
              export MISE_STATE_DIR="$TMPDIR/mise-state"
              export UV_CACHE_DIR="$TMPDIR/uv-cache"

              mise trust --all --yes
              mise run --skip-tools build-backend

              runHook postBuild
            '';

            checkPhase = ''
              runHook preCheck

              ${exportBackendEnv}
              ${exportPythonToolEnv}
              export CARGO_HOME="$TMPDIR/cargo-home"
              export MISE_CACHE_DIR="$TMPDIR/mise-cache"
              export MISE_CONFIG_DIR="$TMPDIR/mise-config"
              export MISE_DATA_DIR="$TMPDIR/mise-data"
              export MISE_STATE_DIR="$TMPDIR/mise-state"
              export UV_CACHE_DIR="$TMPDIR/uv-cache"

              mise run --skip-tools test-backend

              runHook postCheck
            '';

            installPhase = ''
              runHook preInstall

              mkdir -p "$out/bin" "$out/python/units"
              cp build/tools/units-opt "$out/bin/units-opt"
              cp frontend/python/src/units/_units_backend*.so "$out/python/units/"

              runHook postInstall
            '';
          };

          mkFrontendCheck =
            name: task:
            llvm.stdenv.mkDerivation {
              pname = "units-${name}-check";
              version = "0.0.0";
              src = self;

              nativeBuildInputs = [
                pkgs.mise
                frontendPythonEnv
                backendPackage
              ];

              dontConfigure = true;

              buildPhase = ''
                runHook preBuild

                export HOME="$TMPDIR/home"
                export MISE_CACHE_DIR="$TMPDIR/mise-cache"
                export MISE_CONFIG_DIR="$TMPDIR/mise-config"
                export MISE_DATA_DIR="$TMPDIR/mise-data"
                export MISE_STATE_DIR="$TMPDIR/mise-state"
                export UV_CACHE_DIR="$TMPDIR/uv-cache"
                ${exportUvEnv}
                export UNITS_NIX_PYTHON=1

                mkdir -p "$HOME" frontend/python/src/units
                cp ${backendPackage}/python/units/_units_backend*.so frontend/python/src/units/

                mise trust --all --yes
                mise run --skip-tools --skip-deps ${task}

                runHook postBuild
              '';

              installPhase = ''
                mkdir -p "$out"
                touch "$out/${name}-check-passed"
              '';
            };
        in
        {
          packages.backend = backendPackage;

          checks = {
            backend = backendPackage;
            frontend = mkFrontendCheck "frontend" "//frontend/python:test";
            linting = mkFrontendCheck "frontend" "//:lint";
          };

          devShells.default = pkgs.mkShell {
            packages = [ ]
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

      perSystem = forAllSystems mkSystemOutputs;
    in
    {
      packages = lib.mapAttrs (_system: outputs: outputs.packages) perSystem;
      checks = lib.mapAttrs (_system: outputs: outputs.checks) perSystem;
      devShells = lib.mapAttrs (_system: outputs: outputs.devShells) perSystem;
    };
}
