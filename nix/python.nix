{
  pkgs,
  src,
  pyproject-nix,
  uv2nix,
  pyproject-build-systems,
}:
let
  lib = pkgs.lib;
  workspace = uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = src;
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

  mlirPythonRuntimeEnv = python.withPackages (ps: [
    ps.numpy
    ps.ml-dtypes
    ps.typing-extensions
  ]);

  uvEnv = {
    UV_PYTHON = "${python}/bin/python3";
    UV_PYTHON_DOWNLOADS = "never";
  };
in
{
  inherit
    python
    devtoolsPythonEnv
    frontendPythonEnv
    mlirPythonRuntimeEnv
    uvEnv
    ;
}
