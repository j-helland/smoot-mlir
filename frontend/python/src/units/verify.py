from typing import TYPE_CHECKING, Any, Callable, TypeAlias

if TYPE_CHECKING:
    AnyCallable: TypeAlias = Callable[..., Any]


def verify(fn: AnyCallable) -> AnyCallable:
    return fn
