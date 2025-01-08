import asyncio
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
    A protocol for an injected client. This protocol is used for classes, such as
    Effect, which are defined downstream of the client class, but which depend on
    client instances.
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
