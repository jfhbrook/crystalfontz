import asyncio
from typing import Any, Self, Set, Tuple, TypeVar

from crystalfontz.response import Response

R = TypeVar("R", bound=Response)
Result = Tuple[Exception, None] | Tuple[None, R]


class Receiver(asyncio.Queue[Result[R]]):
    def __init__(self: Self, receiving: "Set[Receiver[Any]]", maxsize=0) -> None:
        super().__init__(maxsize)
        self._receiving = receiving

    async def get(self: Self) -> Result[R]:
        self._receiving.add(self)
        rv = await super().get()
        self._receiving.remove(self)
        return rv
