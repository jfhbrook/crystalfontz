import asyncio
from typing import Any, Self, Set, Tuple, TypeVar

from crystalfontz.response import Response

R = TypeVar("R", bound=Response)
Result = Tuple[Exception, None] | Tuple[None, R]


class Receiver(asyncio.Queue[Result[R]]):
    def __init__(self: Self, receiving: "Set[Receiver[Any]]", maxsize=0) -> None:
        super().__init__(maxsize)
        self._receiving = receiving

    def _set_receiving(self: Self) -> None:
        self._receiving.add(self)

    def _set_not_receiving(self: Self) -> None:
        self._receiving.discard(self)

    async def get(self: Self) -> Result[R]:
        self._set_receiving()
        rv = await super().get()
        self._set_not_receiving()
        return rv
