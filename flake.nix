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

          llvmBase = pkgs.llvmPackages_22;
          llvm = llvmBase // { inherit mlir; };

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

          mlirPythonBuildEnv = python.withPackages (ps: [
            ps.nanobind
            ps.numpy
            ps.ml-dtypes
            ps.pyyaml
            ps.typing-extensions
          ]);

          mlir = llvmBase.mlir.overrideAttrs (old: {
            nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
              mlirPythonBuildEnv
            ];

            cmakeFlags = (old.cmakeFlags or [ ]) ++ [
              "-DMLIR_ENABLE_BINDINGS_PYTHON=ON"
              "-DMLIR_LINK_MLIR_DYLIB=OFF"
              "-DPython_EXECUTABLE=${mlirPythonBuildEnv}/bin/python3"
              "-DPython3_EXECUTABLE=${mlirPythonBuildEnv}/bin/python3"
              "-DMLIR_BINDINGS_PYTHON_INSTALL_PREFIX=python_packages/mlir_core/mlir"
            ];

            postInstall = (old.postInstall or "") + lib.optionalString pkgs.stdenv.hostPlatform.isDarwin ''
              for library in \
                libMLIRPythonCAPI.dylib \
                libMLIRPythonSupport-mlir.dylib \
                libnanobind-mlir.dylib
              do
                ln -s \
                  "../python_packages/mlir_core/mlir/_mlir_libs/$library" \
                  "$out/lib/$library"
              done
            '';
          });

          mlirPythonRuntimeEnv = python.withPackages (ps: [
            ps.numpy
            ps.ml-dtypes
            ps.typing-extensions
          ]);

          mlirPythonPath =
            "${mlir}/python_packages/mlir_core:"
            + "${mlirPythonRuntimeEnv}/${python.sitePackages}";

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
            export NANOBIND_DIR="$("$PYTHON_EXE" -m nanobind --cmake_dir)"
            export LIT_EXE="${devtoolsPythonEnv}/bin/lit"
          '';

          backendPackage = llvm.stdenv.mkDerivation {
            pname = "units-backend";
            version = "0.0.0";
            src = self;

            nativeBuildInputs = backendNativeBuildInputs ++ [ pkgs.rustPlatform.cargoSetupHook ];
            buildInputs = backendBuildInputs;

            # TODO(jwh): Remove once smoot is published as a regular crate.
            # Cargo runs inside the Nix build sandbox, so fetch dependencies first.
            cargoRoot = "units-rs";
            cargoDeps = pkgs.rustPlatform.importCargoLock {
              lockFile = ./units-rs/Cargo.lock;
              outputHashes = {
                "smoot-rs-0.1.0" = "sha256-qwsWZa2OFtqG1dEUQwooESXyqzF7F9zFGBA6dVMC2nc=";
              };
            };
            CARGO_NET_OFFLINE = "true";

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
                pkgs.uv
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
                export UV_PROJECT_ENVIRONMENT="${frontendPythonEnv}"
                export UV_NO_SYNC=1
                export PYTHONPATH="$PWD/frontend/python/src:${mlirPythonPath}"

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
          packages.mlir = mlir;

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

              # Expose MLIR and its runtime dependencies to the uv environment.
              export PYTHONPATH="${mlirPythonPath}"
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
