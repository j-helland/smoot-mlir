# -*- Python -*-

import os

import lit.formats
import lit.util
from lit.llvm import llvm_config
from lit.llvm.subst import FindTool, ToolSubst

# Configuration file for the 'lit' test runner.

# name: The name of this test suite.
config.name = "MLIR_UNITS"

config.test_format = lit.formats.ShTest(not llvm_config.use_lit_shell)

# suffixes: A list of file extensions to treat as test files.
config.suffixes = [".mlir"]

# test_source_root: The root path where tests are located.
config.test_source_root = os.path.dirname(__file__)

# test_exec_root: The root path where tests should be run.
config.test_exec_root = os.path.join(config.project_binary_dir, "tests")

config.substitutions.append(("%PATH%", config.environment["PATH"]))
config.substitutions.append(("%shlibext", config.llvm_shlib_ext))
config.substitutions.append(("%project_source_dir", config.project_source_dir))

llvm_config.with_system_environment(["HOME", "INCLUDE", "LIB", "TMP", "TEMP"])

# excludes: A list of directories to exclude from the testsuite. The 'Inputs'
# subdirectories contain auxiliary inputs for various tests in their parent
# directories.
config.excludes = ["Inputs", "Examples", "CMakeLists.txt", "README.txt", "LICENSE.txt"]

# test_exec_root: The root path where tests should be run.
config.test_exec_root = os.path.join(config.project_binary_dir, "test")
config.project_tools_dir = os.path.join(config.project_binary_dir, "tools")

# Keep project, MLIR, and LLVM tool directories distinct. In the Nix shell,
# FileCheck/count/not come from LLVM_TOOLS_DIR, while mlir-opt/mlir-runner come
# from MLIR_TOOLS_DIR and units-opt is built in project_tools_dir.
llvm_config.with_environment("PATH", config.llvm_tools_dir, append_path=True)
llvm_config.with_environment("PATH", config.mlir_tools_dir, append_path=True)
llvm_config.with_environment("PATH", config.project_tools_dir, append_path=True)

tool_dirs = [config.project_tools_dir, config.mlir_tools_dir, config.llvm_tools_dir]
# Use explicit %tool substitutions before default LLVM substitutions. Otherwise
# `%FileCheck` can be partially rewritten as `%/path/to/FileCheck`.
tools = [
    ToolSubst("%units-opt", command=FindTool("units-opt"), unresolved="fatal"),
    ToolSubst("%mlir-opt", command=FindTool("mlir-opt"), unresolved="fatal"),
    ToolSubst("%mlir-runner", command=FindTool("mlir-runner"), unresolved="fatal"),
    ToolSubst("%FileCheck", command=FindTool("FileCheck"), unresolved="fatal"),
    ToolSubst("%count", command=FindTool("count"), unresolved="fatal"),
    ToolSubst("%not", command=FindTool("not"), unresolved="fatal"),
]

llvm_config.add_tool_substitutions(tools, tool_dirs)
llvm_config.use_default_substitutions()
