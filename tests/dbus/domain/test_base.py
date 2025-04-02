from typing import Any, Callable, List, Union

import pytest

from crystalfontz.dbus.domain.base import (
    array,
    ByteM,
    OptFloatM,
    struct,
    t,
    TypeProtocol,
)


@pytest.mark.parametrize(
    "fn,args,signature",
    [
        (t, ["s", "b", ByteM, OptFloatM], "sbyd"),
        (struct, ["sss"], "(sss)"),
        (array, ["b"], "ab"),
    ],
)
def test_signature_fn(
    fn: Callable[[Any], str], args: List[Union[str, TypeProtocol]], signature: str
) -> None:
    assert fn(*args) == signature
