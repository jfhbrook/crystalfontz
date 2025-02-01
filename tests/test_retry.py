import asyncio
from typing import Optional, Self

import pytest

from crystalfontz.client import retry, timeout


class MockClient:
    def __init__(self: Self) -> None:
        self.times = 0
        self._default_timeout = 0.1
        self._default_retry_times: int = 0

    def reset(self: Self) -> None:
        self.times = 0

    @timeout
    async def test_timeout(self: Self, timeout: Optional[float] = None) -> None:
        to = timeout if timeout is not None else self._default_timeout
        self.times += 1

        if to == float("inf"):
            to = 0

        # Trigger a timeout
        await asyncio.sleep(to + 0.1)

    @retry
    async def test_retry(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> None:
        await self.test_timeout(timeout)


@pytest.mark.asyncio
async def test_retry() -> None:
    client = MockClient()

    with pytest.raises(TimeoutError):
        await client.test_retry()

    assert client.times == 1

    client.reset()

    with pytest.raises(TimeoutError):
        await client.test_retry(retry_times=2)

    assert client.times == 3

    client.reset()

    await client.test_timeout(timeout=float("inf"))
