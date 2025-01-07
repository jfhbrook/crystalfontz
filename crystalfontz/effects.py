from abc import ABC, abstractmethod
import asyncio
import random
import time
from typing import Any, Iterable, Optional, Protocol, Set, Tuple, Type, TypeVar

try:
    from typing import Self
except ImportError:
    Self = Any

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate
from crystalfontz.character import SpecialCharacter
from crystalfontz.cursor import CursorStyle
from crystalfontz.device import Device, DeviceStatus
from crystalfontz.gpio import GpioSettings
from crystalfontz.keys import KeyPress
from crystalfontz.lcd import LcdRegister
from crystalfontz.response import (
    AtxPowerSwitchFunctionalitySet,
    BacklightSet,
    BaudRateSet,
    BootStateStored,
    ClearedScreen,
    CommandSentToLcdController,
    ContrastSet,
    CursorPositionSet,
    CursorStyleSet,
    DataSent,
    DowDeviceInformation,
    DowTransactionResult,
    GpioRead,
    GpioSet,
    KeypadPolled,
    KeyReportingConfigured,
    LcdMemory,
    Line1Set,
    Line2Set,
    LiveTemperatureDisplaySetUp,
    Pong,
    PowerResponse,
    Response,
    SpecialCharacterDataSet,
    TemperatureReportingSetUp,
    UserFlashAreaRead,
    UserFlashAreaWritten,
    Versions,
    WatchdogConfigured,
)
from crystalfontz.temperature import TemperatureDisplayItem

R = TypeVar("R", bound=Response)
Result = Tuple[Exception, None] | Tuple[None, R]


class ClientProtocol(Protocol):
    """
    A protocol for an injected client.
    """

    device: Device
    _default_timeout: float
    _default_retry_times: int

    def subscribe(self: Self, cls: Type[R]) -> asyncio.Queue[Result[R]]: ...

    def unsubscribe(self: Self, cls: Type[R], q: asyncio.Queue[Result[R]]) -> None: ...

    async def ping(
        self: Self,
        payload: bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Pong: ...

    async def versions(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> Versions: ...

    async def write_user_flash_area(
        self: Self,
        data: bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> UserFlashAreaWritten: ...

    async def read_user_flash_area(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> UserFlashAreaRead: ...

    async def store_boot_state(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> BootStateStored: ...

    async def reboot_lcd(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> PowerResponse: ...

    async def reset_host(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> PowerResponse: ...

    async def shutdown_host(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> PowerResponse: ...

    async def clear_screen(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> ClearedScreen: ...

    async def set_line_1(
        self: Self,
        line: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Line1Set: ...

    async def set_line_2(
        self: Self,
        line: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Line2Set: ...

    async def set_special_character_data(
        self: Self,
        index: int,
        character: SpecialCharacter,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> SpecialCharacterDataSet: ...

    def set_special_character_encoding(
        self: Self,
        character: str,
        index: int,
    ) -> None: ...

    async def read_lcd_memory(
        self: Self,
        address: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> LcdMemory: ...

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
        lcd_brightness: int,
        keypad_brightness: Optional[int] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> BacklightSet: ...

    async def read_dow_device_information(
        self: Self,
        index: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DowDeviceInformation: ...

    async def setup_temperature_reporting(
        self: Self,
        enabled: Iterable[int],
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> TemperatureReportingSetUp: ...

    async def dow_transaction(
        self: Self,
        index: int,
        bytes_to_read: int,
        data_to_write: bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DowTransactionResult: ...

    async def setup_live_temperature_display(
        self: Self,
        slot: int,
        item: TemperatureDisplayItem,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> LiveTemperatureDisplaySetUp: ...

    async def send_command_to_lcd_controller(
        self: Self,
        location: LcdRegister,
        data: int | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CommandSentToLcdController: ...

    async def configure_key_reporting(
        self: Self,
        when_pressed: Set[KeyPress],
        when_released: Set[KeyPress],
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> KeyReportingConfigured: ...

    async def poll_keypad(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> KeypadPolled: ...

    async def set_atx_power_switch_functionality(
        self: Self,
        settings: AtxPowerSwitchFunctionalitySettings,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> AtxPowerSwitchFunctionalitySet: ...

    async def configure_watchdog(
        self: Self,
        timeout_seconds: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> WatchdogConfigured: ...

    async def read_status(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> DeviceStatus: ...

    async def send_data(
        self: Self,
        row: int,
        column: int,
        data: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DataSent: ...

    async def set_baud_rate(
        self: Self,
        baud_rate: BaudRate,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> BaudRateSet: ...

    async def set_gpio(
        self: Self,
        index: int,
        output_state: int,
        settings: GpioSettings,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> GpioSet: ...

    async def read_gpio(
        self: Self,
        index: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> GpioRead: ...


class Effect(ABC):
    """
    An effect. Effects are time-based actions implemented on top of the client,
    such as marquees and screensavers.
    """

    def __init__(
        self: Self,
        client: ClientProtocol,
        tick: float = 1.0,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        _loop = loop if loop else asyncio.get_running_loop()
        self._event_loop: asyncio.AbstractEventLoop = _loop

        self.client: ClientProtocol = client
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
        row: int,
        text: str,
        client: ClientProtocol,
        pause: Optional[float] = None,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        device = client.device

        if not (0 <= row < device.lines):
            raise ValueError(f"Invalid row: {row}")

        self._timeout = timeout if timeout is not None else client._default_timeout
        self._retry_times = (
            retry_times if retry_times is not None else client._default_retry_times
        )

        _tick = tick if tick is not None else 0.3

        super().__init__(client=client, tick=_tick, loop=loop)
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
        await self.client.send_data(self.row, 0, buffer)
        self.shift += 1
        if self.shift >= device.columns:
            self.shift = 0

    def _line(self: Self) -> bytes:
        device = self.client.device

        left: bytes = self.text[self.shift :]
        right: bytes = self.text[0 : self.shift]
        middle: bytes = b" " * max(device.columns - len(self.text), 1)
        return (left + middle + right)[0 : device.columns]


class Screensaver(Effect):
    def __init__(
        self: Self,
        text: str,
        client: ClientProtocol,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        device = client.device
        buffer = device.character_rom.encode(text)

        if len(buffer) >= device.columns:
            raise ValueError(
                f"Text length {len(buffer)} is too long to fit onto the device's "
                f"{device.columns} columns"
            )

        super().__init__(
            client=client, tick=tick if tick is not None else 3.0, loop=loop
        )

        self.text: bytes = buffer

    async def render(self: Self) -> None:
        device = self.client.device

        await self.client.clear_screen()

        row = random.randrange(0, device.lines)
        column = random.randrange(0, device.columns - len(self.text))

        await self.client.send_data(row, column, self.text)
