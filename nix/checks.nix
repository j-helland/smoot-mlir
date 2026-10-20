{
  pkgs,
  src,
  llvm,
  backendPackage,
  frontendPythonEnv,
  mlirPythonPath,
  exportUvEnv,
}:
let
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
  backend = backendPackage;
  frontend = mkFrontendCheck "frontend" "//frontend/python:test";
  linting = mkFrontendCheck "frontend" "//:lint";
}
