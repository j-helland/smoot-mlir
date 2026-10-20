{
  pkgs,
  llvmBase,
  python,
}:
let
  lib = pkgs.lib;
  mlirPythonBuildEnv = python.withPackages (ps: [
    ps.nanobind
    ps.numpy
    ps.ml-dtypes
    ps.pyyaml
    ps.typing-extensions
  ]);
in
llvmBase.mlir.overrideAttrs (old: {
  nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
    mlirPythonBuildEnv
  ];

  cmakeFlags =
    (old.cmakeFlags or [ ])
    ++ [
      "-DMLIR_ENABLE_BINDINGS_PYTHON=ON"
      "-DMLIR_PYTHON_STUBGEN_ENABLED=ON"
      "-DBUILD_SHARED_LIBS=ON"
      "-DMLIR_LINK_MLIR_DYLIB=OFF"
      "-DPython_EXECUTABLE=${mlirPythonBuildEnv}/bin/python3"
      "-DPython3_EXECUTABLE=${mlirPythonBuildEnv}/bin/python3"
      "-DMLIR_BINDINGS_PYTHON_INSTALL_PREFIX=python_packages/mlir_core/mlir"
    ]
    ++ lib.optionals pkgs.stdenv.hostPlatform.isDarwin [
      "-DCMAKE_BUILD_RPATH=@loader_path/../lib"
    ];

  postInstall =
    (old.postInstall or "")
    + lib.optionalString pkgs.stdenv.hostPlatform.isDarwin ''
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
})
