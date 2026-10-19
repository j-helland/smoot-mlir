from collections.abc import Callable

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type


@pytest.fixture
def diagnostic_snapshot(
    snapshot: SnapshotAssertion,
    pytestconfig: pytest.Config,
) -> SnapshotAssertion:
    root = str(pytestconfig.rootpath)
    return snapshot(
        matcher=path_type(
            types=(str,),
            replacer=_redact_path_prefix(root),
        )
    )


def _redact_path_prefix(prefix: str) -> Callable:
    def redact(data: object, _match: object) -> object:
        if isinstance(data, str):
            return data.replace(prefix, "[PATH]")
        return data

    return redact
