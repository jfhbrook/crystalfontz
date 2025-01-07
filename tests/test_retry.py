import asyncio
from typing import Any, Optional

try:
    from typing import Self
except ImportError:
    Self = Any

import pytest

from crystalfontz.client import retry


class MockClient:
    def __init__(self: Self) -> None:
        self.times = 0
        self._default_timeout = 0.1
        self._default_retry_times: int = 0

    def reset(self: Self) -> None:
        self.times = 0

    @retry
    async def test(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> None:
        to = timeout if timeout is not None else self._default_timeout
        self.times += 1

        if to == float("inf"):
            to = 0

        # Trigger a timeout
        await asyncio.sleep(to + 0.1)


@pytest.mark.asyncio
async def test_retry() -> None:
    client = MockClient()

    with pytest.raises(asyncio.TimeoutError):
        await client.test()

    assert client.times == 1

    client.reset()

    with pytest.raises(asyncio.TimeoutError):
        await client.test(retry_times=2)

    assert client.times == 3

    client.reset()

    await client.test(timeout=float("inf"))
