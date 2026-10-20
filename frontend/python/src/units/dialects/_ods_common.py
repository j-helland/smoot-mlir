"""This file is necessary because MLIR TableGen generates imports of the form `from ._ods_common import ...`."""

from mlir.dialects._ods_common import (
    _cext,
    equally_sized_accessor,
    get_default_loc_context,
    get_op_results_or_values,
    segmented_accessor,
)

__all__ = [
    "_cext",
    "equally_sized_accessor",
    "get_default_loc_context",
    "get_op_results_or_values",
    "segmented_accessor",
]
