import lit.formats

config.name = "units-mlir-demo"
config.test_format = lit.formats.ShTest(execute_external=True)
config.suffixes = [".mlir"]

config.test_source_root = config.units_src_root
config.test_exec_root = config.units_obj_root

config.substitutions.append(("%mlir-opt", config.mlir_opt))
config.substitutions.append(("%FileCheck", config.filecheck))
config.substitutions.append(("%units_plugin", config.units_plugin))
