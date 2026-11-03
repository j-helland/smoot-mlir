{
  pkgs,
  src,
  pyproject-nix,
  uv2nix,
  pyproject-build-systems,
}:
let
  llvmBase = pkgs.llvmPackages_22;
  llvm = llvmBase // {
    inherit mlir;
  };

  pythonEnvs = import ./python.nix {
    inherit
      pkgs
      src
      pyproject-nix
      uv2nix
      pyproject-build-systems
      ;
  };

  mlir = import ./mlir.nix {
    inherit pkgs llvmBase;
    inherit (pythonEnvs) python;
  };

  mlirPythonPath =
    "${mlir}/python_packages/mlir_core:"
    + "${pythonEnvs.mlirPythonRuntimeEnv}/${pythonEnvs.python.sitePackages}";

  toolchain = import ./toolchain.nix {
    inherit pkgs llvm;
    inherit (pythonEnvs) devtoolsPythonEnv uvEnv;
  };

  backendPackage = import ./backend.nix {
    inherit pkgs src llvm;
    inherit (toolchain)
      backendNativeBuildInputs
      backendBuildInputs
      exportBackendEnv
      exportPythonToolEnv
      ;
  };

  miseTools = import ./mise-tools.nix { inherit pkgs src; };
in
{
  packages = {
    backend = backendPackage;
    inherit mlir;
  };

  checks = import ./checks.nix {
    inherit
      pkgs
      src
      llvm
      backendPackage
      mlirPythonPath
      miseTools
      ;
    inherit (pythonEnvs) frontendPythonEnv;
    inherit (toolchain)
      backendNativeBuildInputs
      backendBuildInputs
      exportBackendEnv
      exportPythonToolEnv
      exportUvEnv
      ;
  };

  devShells.default = import ./shell.nix {
    inherit pkgs llvm mlirPythonPath;
    inherit (toolchain) backendNativeBuildInputs backendBuildInputs exportBackendEnv;
  };
}
