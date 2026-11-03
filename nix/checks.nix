{
  pkgs,
  src,
  llvm,
  backendPackage,
  frontendPythonEnv,
  mlirPythonPath,
  miseTools,
  backendNativeBuildInputs,
  backendBuildInputs,
  exportBackendEnv,
  exportPythonToolEnv,
  exportUvEnv,
}:
let
  exportMiseEnv = ''
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
    # Writable, so a backend rebuild in the lint check can overwrite it.
    install -m644 ${backendPackage}/python/units/_units_backend*.so frontend/python/src/units/
  '';

  mkFrontendCheck =
    name: task:
    llvm.stdenv.mkDerivation {
      pname = "units-${name}-check";
      version = "0.0.0";
      inherit src;

      nativeBuildInputs = [
        pkgs.mise
        pkgs.uv
        frontendPythonEnv
        backendPackage
      ];

      dontConfigure = true;

      buildPhase = ''
        runHook preBuild

        ${exportMiseEnv}

        mise trust --all --yes
        mise run --skip-tools --skip-deps ${task}

        runHook postBuild
      '';

      installPhase = ''
        mkdir -p "$out"
        touch "$out/${name}-check-passed"
      '';
    };

  # Lint tasks are aggregates of other tasks, so they must run with their
  # dependencies. That includes a backend build for clang-tidy's compile
  # database.
  lintCheck = llvm.stdenv.mkDerivation {
    pname = "units-linting-check";
    version = "0.0.0";
    inherit src;

    nativeBuildInputs = backendNativeBuildInputs ++ [
      pkgs.rustPlatform.cargoSetupHook
      pkgs.cargo-shear
      pkgs.cargo-sort
      miseTools.ruff
      miseTools.ty
      frontendPythonEnv
    ];
    buildInputs = backendBuildInputs;

    inherit (backendPackage) cargoRoot cargoDeps CARGO_NET_OFFLINE;

    dontConfigure = true;

    buildPhase = ''
      runHook preBuild

      ${exportBackendEnv}
      ${exportPythonToolEnv}
      ${exportMiseEnv}
      export CARGO_HOME="$TMPDIR/cargo-home"
      # Make `uv python find` (used by ty) pick the frontend env over devtools.
      export VIRTUAL_ENV="${frontendPythonEnv}"

      # Lint tasks enumerate files with `git ls-files`; the source has no .git.
      git init --quiet
      git add --all

      mise trust --all --yes
      mise run --skip-tools //:lint

      runHook postBuild
    '';

    installPhase = ''
      mkdir -p "$out"
      touch "$out/linting-check-passed"
    '';
  };
in
{
  backend = backendPackage;
  frontend = mkFrontendCheck "frontend" "//frontend/python:test";
  linting = lintCheck;
}
