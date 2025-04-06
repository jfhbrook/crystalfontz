import asyncio
from typing import Dict, Self

from crystalfontz.effects import Effect

Handle = int


class EffectManager:
    def __init__(self: Self) -> None:
        self._handle: Handle = -1
        self._effects: Dict[Handle, Effect] = dict()
        self._tasks: Dict[Handle, asyncio.Task[None]] = dict()

    def next_handle(self: Self) -> Handle:
        self._handle += 1
        return self._handle

    def add(self: Self, effect: Effect) -> None:
        handle = self.next_handle()
        self._effects[handle] = effect
        self._tasks[handle] = asyncio.create_task(effect.run())

    async def remove(self: Self, handle: Handle) -> None:
        task = self._tasks[handle]
        self._effects[handle].stop()
        del self._effects[handle]
        del self._tasks[handle]

        await task

    async def remove_all(self: Self) -> None:
        await asyncio.gather(*[self.remove(handle) for handle in self._effects.keys()])
