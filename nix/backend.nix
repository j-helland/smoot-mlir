{
  pkgs,
  src,
  llvm,
  devtoolsPythonEnv,
  backendNativeBuildInputs,
  backendBuildInputs,
  exportBackendEnv,
}:
let
  exportPythonToolEnv = ''
    export PYTHON_EXE="${devtoolsPythonEnv}/bin/python3"
    export NANOBIND_DIR="$("$PYTHON_EXE" -m nanobind --cmake_dir)"
    export LIT_EXE="${devtoolsPythonEnv}/bin/lit"
  '';
in
llvm.stdenv.mkDerivation {
  pname = "units-backend";
  version = "0.0.0";
  inherit src;

  nativeBuildInputs = backendNativeBuildInputs ++ [ pkgs.rustPlatform.cargoSetupHook ];
  buildInputs = backendBuildInputs;

  # TODO(jwh): Remove once smoot is published as a regular crate.
  # Cargo runs inside the Nix build sandbox, so fetch dependencies first.
  cargoRoot = "units-rs";
  cargoDeps = pkgs.rustPlatform.importCargoLock {
    lockFile = "${src}/units-rs/Cargo.lock";
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
}
