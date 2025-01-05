import asyncio
from collections import defaultdict
import logging
from typing import cast, Dict, Iterable, List, Optional, Self, Set, Type, TypeVar

from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate
from crystalfontz.character import SpecialCharacter
from crystalfontz.command import (
    ClearScreen,
    Command,
    ConfigureKeyReporting,
    ConfigureWatchdog,
    DowTransaction,
    GetVersions,
    Ping,
    Poke,
    PollKeypad,
    ReadDowDeviceInformation,
    ReadGpio,
    ReadStatus,
    ReadUserFlashArea,
    RebootLCD,
    ResetHost,
    SendCommandToLcdController,
    SendData,
    SetAtxPowerSwitchFunctionality,
    SetBacklight,
    SetBaudRate,
    SetContrast,
    SetCursorPosition,
    SetCursorStyle,
    SetGpio,
    SetLine1,
    SetLine2,
    SetSpecialCharacterData,
    SetupLiveTemperatureDisplay,
    SetupTemperatureReporting,
    ShutdownHost,
    StoreBootState,
    WriteUserFlashArea,
)
from crystalfontz.cursor import CursorStyle
from crystalfontz.device import Device, DeviceStatus, lookup_device
from crystalfontz.effects import Marquee, Screensaver
from crystalfontz.error import ConnectionError
from crystalfontz.gpio import GpioSettings
from crystalfontz.keys import KeyPress
from crystalfontz.lcd import LcdRegister
from crystalfontz.packet import Packet, parse_packet, serialize_packet
from crystalfontz.report import NoopReportHandler, ReportHandler
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
    KeyActivityReport,
    KeypadPolled,
    KeyReportingConfigured,
    Line1Set,
    Line2Set,
    LiveTemperatureDisplaySetUp,
    Poked,
    Pong,
    PowerResponse,
    RawResponse,
    Response,
    SpecialCharacterDataSet,
    StatusRead,
    TemperatureReport,
    TemperatureReportingSetUp,
    UserFlashAreaRead,
    UserFlashAreaWritten,
    Versions,
    WatchdogConfigured,
)
from crystalfontz.temperature import TemperatureDisplayItem

logger = logging.getLogger(__name__)

R = TypeVar("R", bound=Response)


class Client(asyncio.Protocol):
    def __init__(
        self: Self,
        device: Device,
        report_handler: ReportHandler,
        loop: asyncio.AbstractEventLoop,
    ) -> None:

        self.device: Device = device
        self._report_handler: ReportHandler = report_handler

        self._buffer: bytes = b""
        self._loop: asyncio.AbstractEventLoop = loop
        self._transport: Optional[SerialTransport] = None
        self._connection_made: asyncio.Future[None] = self._loop.create_future()

        self._lock: asyncio.Lock = asyncio.Lock()
        self._expect: Optional[Type[Response]] = None
        self._queues: Dict[Type[Response], List[asyncio.Queue[Response]]] = defaultdict(
            lambda: list()
        )

    #
    # pyserial callbacks
    #

    def connection_made(self: Self, transport) -> None:
        if not isinstance(transport, SerialTransport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport
        self._running = True

        self._key_activity_queue: asyncio.Queue[KeyActivityReport] = self.subscribe(
            KeyActivityReport
        )
        self._temperature_queue: asyncio.Queue[TemperatureReport] = self.subscribe(
            TemperatureReport
        )

        asyncio.create_task(self._handle_key_activity())
        asyncio.create_task(self._handle_temperature())

        self._connection_made.set_result(None)

    def connection_lost(self: Self, exc: Optional[Exception]) -> None:
        self._running = False
        if exc:
            raise ConnectionError("Connection lost") from exc

    def close(self: Self) -> None:
        self._running = False
        if self._transport:
            self._transport.close()

    def data_received(self: Self, data: bytes) -> None:
        self._buffer += data

        packet, buff = parse_packet(self._buffer)
        self._buffer = buff

        while packet:
            self._packet_received(packet)
            packet, buff = parse_packet(self._buffer)
            self._buffer = buff

    def _packet_received(self: Self, packet: Packet) -> None:
        res = Response.from_packet(packet)
        if type(res) in self._queues:
            for q in self._queues[type(res)]:
                q.put_nowait(res)

        self._handle_raw_subscriptions(packet)

    def _handle_raw_subscriptions(self: Self, packet: Packet) -> None:
        if RawResponse in self._queues:
            raw_res = RawResponse.from_packet(packet)
            for q in self._queues[RawResponse]:
                q.put_nowait(raw_res)

    #
    # Event subscriptions
    #

    def subscribe[R](self: Self, cls: Type[R]) -> asyncio.Queue[R]:
        q: asyncio.Queue[R] = asyncio.Queue()
        self._queues[cast(Type[Response], cls)].append(cast(asyncio.Queue[Response], q))
        return q

    def unsubscribe[R](self: Self, cls: Type[R], q: asyncio.Queue[R]) -> None:
        key = cast(Type[Response], cls)
        self._queues[key] = cast(
            List[asyncio.Queue[Response]],
            [q_ for q_ in self._queues[key] if q_ != cast(asyncio.Queue[Response], q)],
        )

    async def expect[R](self: Self, cls: Type[R]) -> R:
        q = self.subscribe(cls)
        res = await q.get()
        self.unsubscribe(cls, q)
        return res

    #
    # Commands
    #

    async def send_command[R](self: Self, command: Command, response_cls: Type[R]) -> R:
        async with self._lock:
            self.send_packet(command.to_packet())
            return await self.expect(response_cls)

    def send_packet(self: Self, packet: Packet) -> None:
        if not self._transport:
            raise ConnectionError("Must be connected to send data")
        buff = serialize_packet(packet)
        self._transport.write(buff)

    async def ping(self: Self, payload: bytes) -> Pong:
        return await self.send_command(Ping(payload), Pong)

    async def versions(self: Self) -> Versions:
        return await self.send_command(GetVersions(), Versions)

    async def load_device(self: Self) -> None:
        versions = await self.versions()
        self.device = lookup_device(
            versions.model, versions.hardware_rev, versions.firmware_rev
        )

    async def write_user_flash_area(self: Self, data: bytes) -> UserFlashAreaWritten:
        return await self.send_command(WriteUserFlashArea(data), UserFlashAreaWritten)

    async def read_user_flash_area(self: Self) -> UserFlashAreaRead:
        return await self.send_command(ReadUserFlashArea(), UserFlashAreaRead)

    async def store_boot_state(self: Self) -> BootStateStored:
        return await self.send_command(StoreBootState(), BootStateStored)

    async def reboot_lcd(self: Self) -> PowerResponse:
        return await self.send_command(RebootLCD(), PowerResponse)

    async def reset_host(self: Self) -> PowerResponse:
        await self.send_command(ResetHost(), PowerResponse)
        return await self.expect(PowerResponse)

    async def shutdown_host(self: Self) -> PowerResponse:
        return await self.send_command(ShutdownHost(), PowerResponse)

    async def clear_screen(self: Self) -> ClearedScreen:
        return await self.send_command(ClearScreen(), ClearedScreen)

    async def set_line_1(self: Self, line: str | bytes) -> Line1Set:
        return await self.send_command(SetLine1(line, self.device), Line1Set)

    async def set_line_2(self: Self, line: str | bytes) -> Line2Set:
        return await self.send_command(SetLine2(line, self.device), Line2Set)

    async def set_special_character_data(
        self: Self, index: int, character: SpecialCharacter, as_: Optional[str] = None
    ) -> SpecialCharacterDataSet:
        return await self.send_command(
            SetSpecialCharacterData(index, character, self.device),
            SpecialCharacterDataSet,
        )

    def set_special_character_encoding(self: Self, character: str, index: int) -> None:
        self.device.character_rom.set_encoding(character, index)

    async def poke(self: Self, address: int) -> Poked:
        return await self.send_command(Poke(address), Poked)

    async def set_cursor_position(
        self: Self, row: int, column: int
    ) -> CursorPositionSet:
        return await self.send_command(
            SetCursorPosition(row, column, self.device), CursorPositionSet
        )

    async def set_cursor_style(self: Self, style: CursorStyle) -> CursorStyleSet:
        return await self.send_command(SetCursorStyle(style), CursorStyleSet)

    async def set_contrast(self: Self, contrast: float) -> ContrastSet:
        return await self.send_command(SetContrast(contrast, self.device), ContrastSet)

    async def set_backlight(
        self: Self, lcd_brightness: float, keypad_brightness: Optional[float] = None
    ) -> BacklightSet:
        return await self.send_command(
            SetBacklight(lcd_brightness, keypad_brightness, self.device), BacklightSet
        )

    async def read_dow_device_information(
        self: Self, index: int
    ) -> DowDeviceInformation:
        return await self.send_command(
            ReadDowDeviceInformation(index), DowDeviceInformation
        )

    async def setup_temperature_reporting(
        self: Self, enabled: Iterable[int]
    ) -> TemperatureReportingSetUp:
        return await self.send_command(
            SetupTemperatureReporting(enabled, self.device), TemperatureReportingSetUp
        )

    async def dow_transaction(
        self: Self, index: int, bytes_to_read: int, data_to_write: bytes
    ) -> DowTransactionResult:
        return await self.send_command(
            DowTransaction(index, bytes_to_read, data_to_write), DowTransactionResult
        )

    async def setup_live_temperature_display(
        self: Self, slot: int, item: TemperatureDisplayItem
    ) -> LiveTemperatureDisplaySetUp:
        return await self.send_command(
            SetupLiveTemperatureDisplay(slot, item, self.device),
            LiveTemperatureDisplaySetUp,
        )

    async def send_command_to_lcd_controller(
        self: Self, register: LcdRegister, data: int | bytes
    ) -> CommandSentToLcdController:
        return await self.send_command(
            SendCommandToLcdController(register, data), CommandSentToLcdController
        )

    async def configure_key_reporting(
        self: Self, when_pressed: Set[KeyPress], when_released: Set[KeyPress]
    ) -> KeyReportingConfigured:
        return await self.send_command(
            ConfigureKeyReporting(when_pressed, when_released), KeyReportingConfigured
        )

    async def poll_keypad(self: Self) -> KeypadPolled:
        return await self.send_command(PollKeypad(), KeypadPolled)

    async def set_atx_power_switch_functionality(
        self: Self, settings: AtxPowerSwitchFunctionalitySettings
    ) -> AtxPowerSwitchFunctionalitySet:
        return await self.send_command(
            SetAtxPowerSwitchFunctionality(settings), AtxPowerSwitchFunctionalitySet
        )

    async def configure_watchdog(
        self: Self, timeout_seconds: int
    ) -> WatchdogConfigured:
        return await self.send_command(
            ConfigureWatchdog(timeout_seconds), WatchdogConfigured
        )

    async def read_status(self: Self) -> DeviceStatus:
        res = await self.send_command(ReadStatus(), StatusRead)
        return self.device.status(res.data)

    async def send_data(
        self: Self, row: int, column: int, data: str | bytes
    ) -> DataSent:
        return await self.send_command(
            SendData(row, column, data, self.device), DataSent
        )

    async def set_baud_rate(self: Self, baud_rate: BaudRate) -> BaudRateSet:
        res = await self.send_command(SetBaudRate(baud_rate), BaudRateSet)
        if not self._transport or not self._transport.serial:
            raise ConnectionError("Unable to set new baud rate")
        self._transport.serial.baudrate = baud_rate
        return res

    # Older versions of the CFA533 don't support GPIO, and future models might
    # support more GPIO pins. Therefore, we don't validate the index or
    # gatekeep based on
    async def set_gpio(
        self: Self,
        index: int,
        output_state: int,
        settings: Optional[GpioSettings] = None,
    ) -> GpioSet:
        return await self.send_command(SetGpio(index, output_state, settings), GpioSet)

    async def read_gpio(self: Self, index: int) -> GpioRead:
        return await self.send_command(ReadGpio(index), GpioRead)

    #
    # Report handlers
    #

    async def _handle_key_activity(self: Self) -> None:
        while True:
            if not self._running:
                return

            report = await self._key_activity_queue.get()
            await self._report_handler.on_key_activity(report)

    async def _handle_temperature(self: Self) -> None:
        while True:
            if not self._running:
                return

            report = await self._temperature_queue.get()
            await self._report_handler.on_temperature(report)

    #
    # Effects
    #

    def marquee(
        self: Self, row: int, text: str, tick: Optional[float] = None
    ) -> Marquee:
        return Marquee(row, text, client=self, tick=tick, loop=self._loop)

    def screensaver(self: Self, text: str, tick: Optional[float] = None) -> Screensaver:
        return Screensaver(text, client=self, tick=tick, loop=self._loop)


async def create_connection(
    port: str,
    model: str = "CFA533",
    hardware_rev: Optional[str] = None,
    firmware_rev: Optional[str] = None,
    device: Optional[Device] = None,
    report_handler: Optional[ReportHandler] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    baud_rate: BaudRate = 19200,
) -> Client:
    _loop = loop if loop else asyncio.get_running_loop()

    if not device:
        device = lookup_device(model, hardware_rev, firmware_rev)

    if not report_handler:
        report_handler = NoopReportHandler()

    logger.info(f"Connecting to {port} at {baud_rate} baud")

    _, client = await create_serial_connection(
        _loop,
        lambda: Client(device=device, report_handler=report_handler, loop=_loop),
        port,
        baudrate=baud_rate,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
    )

    await client._connection_made

    return client
