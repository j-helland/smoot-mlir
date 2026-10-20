{
  pkgs,
  llvm,
  backendNativeBuildInputs,
  backendBuildInputs,
  exportBackendEnv,
  mlirPythonPath,
}:
pkgs.mkShell {
  packages = [ ] ++ backendNativeBuildInputs ++ backendBuildInputs;

  shellHook = ''
    ${exportBackendEnv}

    export PATH="${llvm.clang-tools}/bin:${llvm.mlir}/bin:${llvm.llvm}/bin:$PATH"

    # Expose MLIR and its runtime dependencies to the uv environment.
    export PYTHONPATH="${mlirPythonPath}"
  '';
}
