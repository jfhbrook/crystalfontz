import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
import functools
import logging
import traceback
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    cast,
    Coroutine,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeGuard,
    TypeVar,
)
import warnings

try:
    from typing import Self
except ImportError:
    Self = Any

from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate, SLOW_BAUD_RATE
from crystalfontz.character import SpecialCharacter
from crystalfontz.command import (
    ClearScreen,
    Command,
    ConfigureKeyReporting,
    ConfigureWatchdog,
    DowTransaction,
    GetVersions,
    Ping,
    PollKeypad,
    ReadDowDeviceInformation,
    ReadGpio,
    ReadLcdMemory,
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
from crystalfontz.error import (
    ConnectionError,
    CrystalfontzError,
    DeviceError,
    ResponseDecodeError,
)
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
    LcdMemory,
    Line1Set,
    Line2Set,
    LiveTemperatureDisplaySetUp,
    Pong,
    PowerResponse,
    RawResponse,
    Response,
    RESPONSE_CLASSES,
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

# 250ms, as per the CFA533 docs. We could add more to account for Linux and Python
# overhead, but the Python overhead is on the order of fractions of a millisecond
# so I'm not worried.
DEFAULT_TIMEOUT = 0.250

# The CFA533 docs suggest retrying, but don't prescribe a particular amount. In
# practice, the CFA533 has proven *very* reliable, so I don't retrying by default
# is necessary.
DEFAULT_RETRY_TIMES = 0

R = TypeVar("R", bound=Response)
Result = Tuple[Exception, None] | Tuple[None, R]
ReportHandlerMethod = Callable[[R], Coroutine[None, None, None]]
T = TypeVar(name="T")


def retry(
    fn: Callable[..., Coroutine[None, None, T]]
) -> Callable[..., Coroutine[None, None, T]]:
    @functools.wraps(fn)
    async def wrapper(self: Any, *args, **kwargs) -> T:
        timeout: float = kwargs.get("timeout", self._default_timeout)
        times: int = kwargs.get("retry_times", self._default_retry_times)
        while True:
            try:
                async with asyncio.timeout(timeout):
                    return await fn(self, *args, **kwargs)
            except TimeoutError as exc:
                if not times:
                    raise exc
                times -= 1
                continue

    return wrapper


class Client(asyncio.Protocol):
    def __init__(
        self: Self,
        device: Device,
        report_handler: ReportHandler,
        timeout: float,
        retry_times: int,
        loop: asyncio.AbstractEventLoop,
    ) -> None:

        self.device: Device = device
        self._report_handler: ReportHandler = report_handler
        self._default_timeout: float = timeout
        self._default_retry_times: int = retry_times

        self._buffer: bytes = b""
        self.loop: asyncio.AbstractEventLoop = loop
        self._transport: Optional[SerialTransport] = None
        self._connection_made: asyncio.Future[None] = self.loop.create_future()
        self.closed: asyncio.Future[None] = self.loop.create_future()

        self._lock: asyncio.Lock = asyncio.Lock()
        self._expect: Optional[Type[Response]] = None
        self._queues: Dict[Type[Response], List[asyncio.Queue[Result[Response]]]] = (
            defaultdict(lambda: list())
        )

    #
    # pyserial callbacks
    #

    def _is_serial_transport(
        self: Self, transport: asyncio.BaseTransport
    ) -> TypeGuard[SerialTransport]:
        return isinstance(transport, SerialTransport)

    def connection_made(self: Self, transport: asyncio.BaseTransport) -> None:
        if not self._is_serial_transport(transport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport
        self._running = True

        self._key_activity_queue: asyncio.Queue[Result[KeyActivityReport]] = (
            self.subscribe(KeyActivityReport)
        )
        self._temperature_queue: asyncio.Queue[Result[TemperatureReport]] = (
            self.subscribe(TemperatureReport)
        )

        self._key_activity_task: asyncio.Task[None] = self.loop.create_task(
            self._handle_report(
                "key_activity",
                self._key_activity_queue,
                self._report_handler.on_key_activity,
            )
        )
        self._temperature_task: asyncio.Task[None] = self.loop.create_task(
            self._handle_report(
                "temperature",
                self._temperature_queue,
                self._report_handler.on_temperature,
            )
        )

        self._connection_made.set_result(None)

    def connection_lost(self: Self, exc: Optional[Exception]) -> None:
        self._running = False
        try:
            if exc:
                raise ConnectionError("Connection lost") from exc
        except Exception as exc:
            self._close(exc)
        else:
            self._close()

    def close(self: Self) -> None:
        """
        Close the connection.
        """
        if self._transport:
            self._transport.close()
        self._close()

    # Internal method to close the connection, potentially due to an exception.
    def _close(self: Self, exc: Optional[Exception] = None) -> None:
        self._running = False

        # A clean exit requires that we cancel these tasks and then wait
        # for them to finish before killing the event loop
        self._key_activity_task.cancel()
        self._temperature_task.cancel()

        tasks_done = asyncio.gather(self._key_activity_task, self._temperature_task)

        def finish() -> None:
            # Tasks successfully closed. Resolve the future if we have it,
            # otherwise raise.
            if self.closed.done():
                if exc:
                    raise exc
            elif exc:
                self.closed.set_exception(exc)
            else:
                self.closed.set_result(None)

        def on_tasks_done(_: asyncio.Future[Tuple[None, None]]) -> None:
            nonlocal exc
            task_exc = tasks_done.exception()
            try:
                # The tasks should have failed with a CancelledError
                if task_exc:
                    raise task_exc
            except asyncio.CancelledError:
                # This error is expected, wrap it up
                finish()
            except Exception as task_exc:
                # An unexpected error of some kind was raised by the tasks.
                # Do our best to handle them...
                if exc:
                    # We have two exceptions. We don't want to mask the
                    # exception that actually caused us to close, so we
                    # warn and hope for the best.
                    warnings.warn(traceback.format_exc())
                else:
                    # This is our new exception.
                    exc = task_exc
                finish()

        tasks_done.add_done_callback(on_tasks_done)

        if self.closed.done() and exc:
            raise exc

    def data_received(self: Self, data: bytes) -> None:
        try:
            self._buffer += data

            packet, buff = parse_packet(self._buffer)
            self._buffer = buff

            while packet:
                self._packet_received(packet)
                packet, buff = parse_packet(self._buffer)
                self._buffer = buff
        except Exception as exc:
            # Exceptions here would have come from the packet parser, not
            # the packet handler
            self._close(exc)

    def _packet_received(self: Self, packet: Packet) -> None:
        logging.debug(f"Packet received: {packet}")
        try:
            res = Response.from_packet(packet)
            raw_res = (
                RawResponse.from_packet(packet) if RawResponse in self._queues else None
            )
        except ResponseDecodeError as exc:
            # We know the intended response type, so send it to any subscribers
            self._emit(exc.response_cls, (exc, None))
        except DeviceError as exc:
            if exc.expected_response in RESPONSE_CLASSES:
                self._emit(RESPONSE_CLASSES[exc.expected_response], (exc, None))
            else:
                self._close(exc)
        except Exception as exc:
            self._close(exc)
        else:
            self._emit(type(res), (None, res))
            if raw_res:
                self._emit(RawResponse, (None, raw_res))

    def _emit(self: Self, response_cls: Type[Response], item: Result[Response]) -> None:
        if response_cls in self._queues:
            for q in self._queues[response_cls]:
                q.put_nowait(item)
        elif item[0]:
            # If we emit a response in a forest and nobody's around to hear it,
            # shut it down and let close handle the exception
            self._close(item[0])

    #
    # Event subscriptions
    #

    def subscribe(self: Self, cls: Type[R]) -> asyncio.Queue[Result[R]]:
        q: asyncio.Queue[Result[R]] = asyncio.Queue()
        key = cast(Type[Response], cls)
        value = cast(asyncio.Queue[Result[Response]], q)
        self._queues[key].append(value)
        return q

    def unsubscribe(self: Self, cls: Type[R], q: asyncio.Queue[Result[R]]) -> None:
        key = cast(Type[Response], cls)
        value = [
            q_
            for q_ in self._queues[key]
            if q_ != cast(asyncio.Queue[Result[Response]], q)
        ]
        cast(List[asyncio.Queue[Result[Response]]], value)
        self._queues[key] = cast(List[asyncio.Queue[Result[Response]]], value)

    @retry
    async def expect(
        self: Self,
        cls: Type[R],
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> R:
        q = self.subscribe(cls)
        exc, res = await q.get()
        q.task_done()
        self.unsubscribe(cls, q)
        if exc:
            raise exc
        elif res:
            return res
        raise CrystalfontzError("assert: result has either exception or response")

    #
    # Commands
    #

    async def send_command(
        self: Self,
        command: Command,
        response_cls: Type[R],
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> R:
        async with self._lock:
            self.send_packet(command.to_packet())
            return await self.expect(
                response_cls, timeout=timeout, retry_times=retry_times
            )

    def send_packet(self: Self, packet: Packet) -> None:
        if not self._transport:
            raise ConnectionError("Must be connected to send data")
        buff = serialize_packet(packet)
        self._transport.write(buff)

    async def ping(
        self: Self,
        payload: bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Pong:
        return await self.send_command(
            Ping(payload), Pong, timeout=timeout, retry_times=retry_times
        )

    async def versions(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Versions:
        return await self.send_command(
            GetVersions(), Versions, timeout=timeout, retry_times=retry_times
        )

    async def load_device(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> None:
        versions = await self.versions(timeout=timeout, retry_times=retry_times)
        self.device = lookup_device(
            versions.model, versions.hardware_rev, versions.firmware_rev
        )

    async def write_user_flash_area(
        self: Self,
        data: bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> UserFlashAreaWritten:
        return await self.send_command(
            WriteUserFlashArea(data),
            UserFlashAreaWritten,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def read_user_flash_area(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> UserFlashAreaRead:
        return await self.send_command(
            ReadUserFlashArea(),
            UserFlashAreaRead,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def store_boot_state(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> BootStateStored:
        return await self.send_command(
            StoreBootState(), BootStateStored, timeout=timeout, retry_times=retry_times
        )

    async def reboot_lcd(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> PowerResponse:
        return await self.send_command(
            RebootLCD(), PowerResponse, timeout=timeout, retry_times=retry_times
        )

    async def reset_host(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> PowerResponse:
        await self.send_command(ResetHost(), PowerResponse)
        return await self.expect(
            PowerResponse, timeout=timeout, retry_times=retry_times
        )

    async def shutdown_host(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> PowerResponse:
        return await self.send_command(
            ShutdownHost(), PowerResponse, timeout=timeout, retry_times=retry_times
        )

    async def clear_screen(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> ClearedScreen:
        return await self.send_command(
            ClearScreen(), ClearedScreen, timeout=timeout, retry_times=retry_times
        )

    async def set_line_1(
        self: Self,
        line: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Line1Set:
        return await self.send_command(
            SetLine1(line, self.device),
            Line1Set,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def set_line_2(
        self: Self,
        line: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Line2Set:
        return await self.send_command(
            SetLine2(line, self.device),
            Line2Set,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def set_special_character_data(
        self: Self,
        index: int,
        character: SpecialCharacter,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> SpecialCharacterDataSet:
        return await self.send_command(
            SetSpecialCharacterData(index, character, self.device),
            SpecialCharacterDataSet,
            timeout=timeout,
            retry_times=retry_times,
        )

    def set_special_character_encoding(
        self: Self,
        character: str,
        index: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> None:
        self.device.character_rom.set_encoding(character, index)

    async def read_lcd_memory(
        self: Self,
        address: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> LcdMemory:
        return await self.send_command(
            ReadLcdMemory(address), LcdMemory, timeout=timeout, retry_times=retry_times
        )

    async def set_cursor_position(
        self: Self,
        row: int,
        column: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CursorPositionSet:
        return await self.send_command(
            SetCursorPosition(row, column, self.device),
            CursorPositionSet,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def set_cursor_style(
        self: Self,
        style: CursorStyle,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CursorStyleSet:
        return await self.send_command(
            SetCursorStyle(style),
            CursorStyleSet,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def set_contrast(
        self: Self,
        contrast: float,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> ContrastSet:
        return await self.send_command(
            SetContrast(contrast, self.device),
            ContrastSet,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def set_backlight(
        self: Self,
        lcd_brightness: float,
        keypad_brightness: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> BacklightSet:
        return await self.send_command(
            SetBacklight(lcd_brightness, keypad_brightness, self.device),
            BacklightSet,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def read_dow_device_information(
        self: Self,
        index: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DowDeviceInformation:
        return await self.send_command(
            ReadDowDeviceInformation(index),
            DowDeviceInformation,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def setup_temperature_reporting(
        self: Self,
        enabled: Iterable[int],
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> TemperatureReportingSetUp:
        return await self.send_command(
            SetupTemperatureReporting(enabled, self.device),
            TemperatureReportingSetUp,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def dow_transaction(
        self: Self,
        index: int,
        bytes_to_read: int,
        data_to_write: bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DowTransactionResult:
        return await self.send_command(
            DowTransaction(index, bytes_to_read, data_to_write),
            DowTransactionResult,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def setup_live_temperature_display(
        self: Self,
        slot: int,
        item: TemperatureDisplayItem,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> LiveTemperatureDisplaySetUp:
        return await self.send_command(
            SetupLiveTemperatureDisplay(slot, item, self.device),
            LiveTemperatureDisplaySetUp,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def send_command_to_lcd_controller(
        self: Self,
        location: LcdRegister,
        data: int | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CommandSentToLcdController:
        return await self.send_command(
            SendCommandToLcdController(location, data),
            CommandSentToLcdController,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def configure_key_reporting(
        self: Self,
        when_pressed: Set[KeyPress],
        when_released: Set[KeyPress],
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> KeyReportingConfigured:
        return await self.send_command(
            ConfigureKeyReporting(when_pressed, when_released),
            KeyReportingConfigured,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def poll_keypad(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> KeypadPolled:
        return await self.send_command(
            PollKeypad(), KeypadPolled, timeout=timeout, retry_times=retry_times
        )

    async def set_atx_power_switch_functionality(
        self: Self,
        settings: AtxPowerSwitchFunctionalitySettings,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> AtxPowerSwitchFunctionalitySet:
        return await self.send_command(
            SetAtxPowerSwitchFunctionality(settings),
            AtxPowerSwitchFunctionalitySet,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def configure_watchdog(
        self: Self,
        timeout_seconds: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> WatchdogConfigured:
        return await self.send_command(
            ConfigureWatchdog(timeout_seconds),
            WatchdogConfigured,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def read_status(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DeviceStatus:
        res = await self.send_command(
            ReadStatus(), StatusRead, timeout=timeout, retry_times=retry_times
        )
        return self.device.status(res.data)

    async def send_data(
        self: Self,
        row: int,
        column: int,
        data: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DataSent:
        return await self.send_command(
            SendData(row, column, data, self.device),
            DataSent,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def set_baud_rate(
        self: Self,
        baud_rate: BaudRate,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> BaudRateSet:
        res = await self.send_command(
            SetBaudRate(baud_rate),
            BaudRateSet,
            timeout=timeout,
            retry_times=retry_times,
        )
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
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> GpioSet:
        return await self.send_command(
            SetGpio(index, output_state, settings),
            GpioSet,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def read_gpio(
        self: Self,
        index: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> GpioRead:
        return await self.send_command(
            ReadGpio(index), GpioRead, timeout=timeout, retry_times=retry_times
        )

    #
    # Report handlers
    #

    async def _handle_report(
        self: Self,
        name: str,
        queue: asyncio.Queue[Result[R]],
        handler: ReportHandlerMethod,
    ) -> None:
        while True:
            if not self._running:
                logging.debug(f"{name} background task exiting")
                return

            logging.debug(f"{name} background task getting a new report")
            exc, report = await queue.get()

            if exc:
                logging.debug(f"{name} background task encountered an exception: {exc}")
                if not self.closed.done():
                    self.closed.set_exception(exc)
                    queue.task_done()
                else:
                    queue.task_done()
                    raise exc
            elif report:
                logging.debug(f"{name} background task is calling {handler.__name__}")
                await handler(report)
                queue.task_done()
            else:
                raise CrystalfontzError(
                    "assert: result has either exception or response"
                )

    #
    # Effects
    #

    def marquee(
        self: Self,
        row: int,
        text: str,
        pause: Optional[float] = None,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Marquee:
        return Marquee(
            row,
            text,
            client=self,
            pause=pause,
            tick=tick,
            timeout=timeout,
            retry_times=retry_times,
            loop=self.loop,
        )

    def screensaver(
        self: Self,
        text: str,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Screensaver:
        return Screensaver(
            text,
            client=self,
            tick=tick,
            timeout=timeout,
            retry_times=retry_times,
            loop=self.loop,
        )


async def create_connection(
    port: str,
    model: str = "CFA533",
    hardware_rev: Optional[str] = None,
    firmware_rev: Optional[str] = None,
    device: Optional[Device] = None,
    report_handler: Optional[ReportHandler] = None,
    timeout: float = DEFAULT_TIMEOUT,
    retry_times: int = DEFAULT_RETRY_TIMES,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    baud_rate: BaudRate = SLOW_BAUD_RATE,
) -> Client:
    _loop = loop if loop else asyncio.get_running_loop()

    if not device:
        device = lookup_device(model, hardware_rev, firmware_rev)

    if not report_handler:
        report_handler = NoopReportHandler()

    logger.info(f"Connecting to {port} at {baud_rate} baud")

    _, client = await create_serial_connection(
        _loop,
        lambda: Client(
            device=device,
            report_handler=report_handler,
            timeout=timeout,
            retry_times=retry_times,
            loop=_loop,
        ),
        port,
        baudrate=baud_rate,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
    )

    await client._connection_made

    return client


@asynccontextmanager
async def client(
    port: str,
    model: str = "CFA533",
    hardware_rev: Optional[str] = None,
    firmware_rev: Optional[str] = None,
    device: Optional[Device] = None,
    report_handler: Optional[ReportHandler] = None,
    timeout: float = DEFAULT_TIMEOUT,
    retry_times: int = DEFAULT_RETRY_TIMES,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    baud_rate: BaudRate = SLOW_BAUD_RATE,
) -> AsyncGenerator[Client, None]:
    client = await create_connection(
        port,
        model=model,
        hardware_rev=hardware_rev,
        firmware_rev=firmware_rev,
        device=device,
        report_handler=report_handler,
        timeout=timeout,
        retry_times=retry_times,
        loop=loop,
        baud_rate=baud_rate,
    )

    yield client

    client.close()
    await client.closed
