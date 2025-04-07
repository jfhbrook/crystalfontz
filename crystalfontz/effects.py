from abc import ABC, abstractmethod
import asyncio
import random
import time
from typing import Optional, Protocol, Self

from crystalfontz.cursor import CursorStyle
from crystalfontz.device import Device
from crystalfontz.response import (
    BacklightSet,
    ClearedScreen,
    ContrastSet,
    CursorPositionSet,
    CursorStyleSet,
    DataSent,
)


class EffectClient(Protocol):
    """
    A protocol for any client used by effects.

    This protocol covers a subset of the `Client` class which may be used by effects.
    """

    device: Device

    async def clear_screen(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> ClearedScreen: ...

    async def set_cursor_position(
        self: Self,
        row: int,
        column: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CursorPositionSet: ...

    async def set_cursor_style(
        self: Self,
        style: CursorStyle,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CursorStyleSet: ...

    async def set_contrast(
        self: Self,
        contrast: float,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> ContrastSet: ...

    async def set_backlight(
        self: Self,
        lcd_brightness: float,
        keypad_brightness: Optional[int] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> BacklightSet: ...

    async def send_data(
        self: Self,
        row: int,
        column: int,
        data: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DataSent: ...


class Effect(ABC):
    """
    An effect. Effects are time-based actions implemented on top of the client,
    such as marquees and screensavers.
    """

    def __init__(
        self: Self,
        client: EffectClient,
        tick: float = 1.0,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        _loop = loop if loop else asyncio.get_running_loop()
        self._event_loop: asyncio.AbstractEventLoop = _loop

        self.timeout: Optional[float] = timeout
        self.retry_times: Optional[int] = retry_times

        self.client: EffectClient = client
        self._running: bool = False
        self._tick: float = tick
        self._task: Optional[asyncio.Task[None]] = None
        self._timer: float = time.time()

    async def run(self: Self) -> None:
        self._running = True

        self.reset_timer()
        await self.start()

        while True:
            self.reset_timer()
            if not self._running:
                await self.finish()
                return
            await self.render()
            await asyncio.sleep(self.time_remaining(self._tick))

    def reset_timer(self: Self) -> None:
        self._timer = time.time()

    @property
    def time_elapsed(self: Self) -> float:
        return time.time() - self._timer

    def time_remaining(self: Self, wait_for: float) -> float:
        return max(wait_for - self.time_elapsed, 0)

    async def sleep_remaining(self: Self, wait_for: float) -> None:
        await asyncio.sleep(self.time_remaining(wait_for))

    async def start(self: Self) -> None:
        pass

    @abstractmethod
    async def render(self: Self) -> None:
        raise NotImplementedError("tick")

    async def finish(self: Self) -> None:
        pass

    def stop(self: Self) -> None:
        self._running = False


class Marquee(Effect):
    """
    A marquee. Prints text to a row, and scrolls it across the screen.
    """

    def __init__(
        self: Self,
        client: EffectClient,
        row: int,
        text: str,
        pause: Optional[float] = None,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        device = client.device

        if not (0 <= row < device.lines):
            raise ValueError(f"Invalid row: {row}")
        _tick = tick if tick is not None else 0.3

        super().__init__(
            client=client,
            tick=_tick,
            timeout=timeout,
            retry_times=retry_times,
            loop=loop,
        )
        self._pause: float = pause if pause is not None else _tick

        self.row: int = row
        self.text: bytes = device.character_rom.encode(text).ljust(device.columns, b" ")
        self.shift: int = 0

    async def start(self: Self) -> None:
        await self.render()
        await self.sleep_remaining(self._pause)

    async def render(self: Self) -> None:
        device = self.client.device
        buffer = self._line()
        await self.client.send_data(
            self.row, 0, buffer, timeout=self.timeout, retry_times=self.retry_times
        )
        self.shift += 1
        if self.shift > device.columns:
            self.shift = 0

    def _line(self: Self) -> bytes:
        device = self.client.device

        left: bytes = self.text[self.shift :]
        right: bytes = self.text[0 : self.shift]
        middle: bytes = b" " * max(device.columns - len(self.text), 1)
        return (left + middle + right)[0 : device.columns]


class Screensaver(Effect):
    """
    A screensaver effect. Prints text at a random position, and moves it around the
    screen on an interval.
    """

    def __init__(
        self: Self,
        client: EffectClient,
        text: str,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        device = client.device
        buffer = device.character_rom.encode(text)

        if len(buffer) > device.columns:
            raise ValueError(
                f"Text length {len(buffer)} is too long to fit onto the device's "
                f"{device.columns} columns"
            )

        super().__init__(
            client=client,
            tick=tick if tick is not None else 3.0,
            timeout=timeout,
            retry_times=retry_times,
            loop=loop,
        )

        self.text: bytes = buffer

    async def render(self: Self) -> None:
        device = self.client.device

        await self.client.clear_screen(
            timeout=self.timeout, retry_times=self.retry_times
        )

        row = random.randrange(0, device.lines)
        column = random.randrange(0, device.columns - len(self.text))

        await self.client.send_data(
            row, column, self.text, timeout=self.timeout, retry_times=self.retry_times
        )


class DanceParty(Effect):
    """
    A dance party effect. Randomly changes the backlight and contrast settings on
    an interval.
    """

    def __init__(
        self: Self,
        client: EffectClient,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(
            client=client,
            tick=tick if tick is not None else 0.5,
            timeout=timeout,
            retry_times=retry_times,
            loop=loop,
        )

    def _random_contrast(self: Self) -> float:
        return random.choice([0.4, 0.5, 0.6])

    def _random_brightness(self: Self) -> float:
        return random.choice([0.2, 0.4, 0.6, 0.8])

    async def render(self: Self) -> None:
        await asyncio.gather(
            self.client.set_contrast(self._random_contrast()),
            self.client.set_backlight(self._random_brightness()),
        )
