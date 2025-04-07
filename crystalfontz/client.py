"""
crystalfontz is a library and CLI for interacting with Crystalfontz LCD displays.
While it has an eye for supporting multiple devices, it was developed against a CFA533.

# Example

```py
import asyncio

from crystalfontz import connection, SLOW_BAUD_RATE


async def main():
    # Will close the client on exit
    async with connection(
        "/dev/ttyUSB0",
        model="CFA533",
        baud_rate=SLOW_BAUD_RATE
    ) as client:
        await client.send_data(0, 0, "Hello world!")

asyncio.run(main())
```

This will write "Hello world!" on the first line of the LCD.
"""

import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
import functools
import logging
import random
from string import ascii_lowercase
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
    Self,
    Set,
    Tuple,
    Type,
    TypeGuard,
    TypeVar,
)
import warnings

from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate, OTHER_BAUD_RATE, SLOW_BAUD_RATE
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
from crystalfontz.effects import DanceParty, Marquee, Screensaver
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
from crystalfontz.receiver import Receiver
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


def timeout(
    fn: Callable[..., Coroutine[None, None, T]],
) -> Callable[..., Coroutine[None, None, T]]:
    @functools.wraps(fn)
    async def wrapper(self: Any, *args, **kwargs) -> T:
        to = kwargs.get("timeout", self._default_timeout)
        to = to if to is not None else self._default_timeout
        assert type(to) is float, "timeout should be a float"
        async with asyncio.timeout(to):
            return await fn(self, *args, **kwargs)

    return wrapper


def retry(
    fn: Callable[..., Coroutine[None, None, T]],
) -> Callable[..., Coroutine[None, None, T]]:
    @functools.wraps(fn)
    async def wrapper(self: Any, *args, **kwargs) -> T:
        times = (
            kwargs.get("retry_times", self._default_retry_times)
            or self._default_retry_times
        )
        assert type(times) is int, "retry_times should be an int"
        while True:
            try:
                return await fn(self, *args, **kwargs)
            except TimeoutError as exc:
                if not times:
                    raise exc
                times -= 1
                continue

    return wrapper


class Client(asyncio.Protocol):
    """
    A crystalfontz client. Typically created through a call to `connection` or
    `create_connection`.

    This client has methods for every command supported by the CFA533. For more
    details, refer to the datasheet for your device.

    In addition, this client will accept a `ReportHandler` class, and will call
    the appropriate method on it whenever a key activity or temperature report is
    received.

    Also supported are configurations for command timeouts and retry behavior. The
    default behavior is a timeout of 0.25 seconds with no retries. This 250ms timeout
    is based on the datasheet for the CFA533.
    """

    def __init__(
        self: Self,
        device: Device,
        report_handler: ReportHandler,
        timeout: float,
        retry_times: int,
        loop: asyncio.AbstractEventLoop,
    ) -> None:

        self.device: Device = device
        self.report_handler: ReportHandler = report_handler
        self._default_timeout: float = timeout
        self._default_retry_times: int = retry_times

        self._buffer: bytes = b""
        self.loop: asyncio.AbstractEventLoop = loop
        self._transport: Optional[SerialTransport] = None
        self._connection_made: asyncio.Future[None] = self.loop.create_future()
        self._closed: asyncio.Future[None] = self.loop.create_future()

        self._lock: asyncio.Lock = asyncio.Lock()
        self._expect: Optional[Type[Response]] = None
        self._receivers: Dict[Type[Response], List[Receiver[Response]]] = defaultdict(
            lambda: list()
        )
        self._receiving: Set[Receiver[Any]] = set()

    @property
    def model(self: Self) -> str:
        """
        The model of the current device.
        """

        return self.device.model

    @property
    def hardware_rev(self: Self) -> str:
        """
        The hardware revision of the current device.
        """

        return self.device.hardware_rev

    @property
    def firmware_rev(self: Self) -> str:
        """
        The firmware revision of the current device.
        """

        return self.device.firmware_rev

    @property
    def baud_rate(self: Self) -> BaudRate:
        """
        The transport's baud rate.
        """

        if not self._transport or not self._transport.serial:
            raise ConnectionError("Uninitialized transport has no baud rate")
        return self._transport.serial.baudrate

    @baud_rate.setter
    def baud_rate(self: Self, baud_rate: BaudRate) -> None:
        if not self._transport or not self._transport.serial:
            raise ConnectionError("Uninitialized transport has no baud rate")
        self._transport.serial.baudrate = baud_rate

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

        self._key_activity_queue: Receiver[KeyActivityReport] = self.subscribe(
            KeyActivityReport, expect=False
        )
        self._temperature_queue: Receiver[TemperatureReport] = self.subscribe(
            TemperatureReport, expect=False
        )

        self._key_activity_task: asyncio.Task[None] = self.loop.create_task(
            self._handle_report(
                "key_activity",
                self._key_activity_queue,
                self.report_handler.on_key_activity,
            )
        )
        self._temperature_task: asyncio.Task[None] = self.loop.create_task(
            self._handle_report(
                "temperature",
                self._temperature_queue,
                self.report_handler.on_temperature,
            )
        )

        self._connection_made.set_result(None)

    def connection_lost(self: Self, exc: Optional[Exception]) -> None:
        self._running = False
        try:
            if exc:
                raise ConnectionError("Connection lost") from exc
        except Exception as exc:
            self._error(exc)
        else:
            self._close()

    @property
    def closed(self: Self) -> asyncio.Future:
        """
        An asyncio.Future that resolves when the connection is closed. This
        may be due either to calling `client.close()` or an Exception.
        """
        return self._closed

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
        tasks_done.add_done_callback(self._finish_tasks(exc))

        if self.closed.done() and exc:
            raise exc

    def _finish_tasks(
        self: Self,
        exc: Optional[Exception],
    ) -> Callable[[asyncio.Future[Tuple[None, None]]], None]:
        def callback(tasks_done: asyncio.Future[Tuple[None, None]]) -> None:
            task_exc = tasks_done.exception()
            try:
                # The tasks should have failed with a CancelledError
                if task_exc:
                    raise task_exc
            except asyncio.CancelledError:
                # This error is expected, wrap it up
                self._finish_close(exc)
            except Exception as task_exc:
                # An unexpected error of some kind was raised by the tasks.
                # Do our best to handle them...
                if exc:
                    # We have two exceptions. We don't want to mask the
                    # exception that actually caused us to close, so we
                    # warn and hope for the best.
                    warnings.warn(traceback.format_exc())
                    self._finish_close(exc)
                else:
                    # This is our new exception.
                    self._finish_close(task_exc)

        return callback

    def _finish_close(self: Self, exc: Optional[BaseException]) -> None:
        # Tasks successfully closed. Resolve the future if we have it,
        # otherwise raise.
        if self.closed.done():
            if exc:
                raise exc
        elif exc:
            self.closed.set_exception(exc)
        else:
            self.closed.set_result(None)

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
            self._error(exc)

    def _error(self: Self, exc: Exception) -> None:
        if self._receiving:
            list(self._receiving)[0].put_nowait((exc, None))
        else:
            self._close(exc)

    def _packet_received(self: Self, packet: Packet) -> None:
        logging.debug(f"Packet received: {packet}")
        try:
            res = Response.from_packet(packet)
            raw_res = (
                RawResponse.from_packet(packet)
                if RawResponse in self._receivers
                else None
            )
        except ResponseDecodeError as exc:
            self._emit_response_decode_error(exc)
        except DeviceError as exc:
            self._emit_device_error(exc)
        except Exception as exc:
            self._error(exc)
        else:
            self._emit(type(res), (None, res))
            if raw_res:
                self._emit(RawResponse, (None, raw_res))

    def _emit(self: Self, response_cls: Type[Response], item: Result[Response]) -> None:
        if response_cls in self._receivers:
            for rcv in self._receivers[response_cls]:
                rcv.put_nowait(item)
        elif item[0]:
            self._error(item[0])

    def _emit_response_decode_error(self: Self, exc: ResponseDecodeError) -> None:
        # We know the intended response type, so send it to any subscribers
        self._emit(exc.response_cls, (exc, None))

    def _emit_device_error(self: Self, exc: DeviceError) -> None:
        if exc.expected_response in RESPONSE_CLASSES:
            self._emit(RESPONSE_CLASSES[exc.expected_response], (exc, None))
        else:
            self._error(exc)

    #
    # Event subscriptions
    #

    def subscribe(self: Self, cls: Type[R], expect: bool = True) -> Receiver[R]:
        """
        Subscribe to results of a given response class. Returns a
        `Receiver[Response]`.

        This is a low level method. Most use cases not met by individual command
        methods or a ReportHandler are best handled with `client.expect`.
        """

        receiving: Set[Receiver[Any]] = self._receiving if expect else set()

        rcv: Receiver[R] = Receiver(receiving)
        key = cast(Type[Response], cls)
        value = cast(Receiver[Response], rcv)
        self._receivers[key].append(value)
        return rcv

    def unsubscribe(self: Self, cls: Type[R], receiver: Receiver[R]) -> None:
        """
        Unsubscribe from results of a given response class and queue. This queue is
        typically created by a call to `client.subscribe`.

        This is a low level method. Most use cases not met by individual command
        methods or a ReportHandler are best handled with `client.expect`.
        """

        key = cast(Type[Response], cls)
        value = [
            rcv
            for rcv in self._receivers[key]
            if rcv != cast(Receiver[Response], receiver)
        ]

        cast_value = cast(List[Receiver[Response]], value)
        self._receivers[key] = cast_value

    @timeout
    async def expect(self: Self, cls: Type[R], timeout: Optional[float] = None) -> R:
        """
        Wait for a response of an expected class, with a timeout.

        This method accepts a `timeout` parameter. If defined, it will override
        the client's default timeout.

        This is a low level method. Most use cases are met by individual command
        methods.
        """
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

    @retry
    async def send_command(
        self: Self,
        command: Command,
        response_cls: Type[R],
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> R:
        """
        Send a `Command`, then wait for and return its expected `Response`.

        This method accepts `timeout` and `retry_times` parameters. If defined, they
        will override the client's default timeout.

        This is a low level method. Most use cases are met by individual command
        methods.
        """
        async with self._lock:
            self.send_packet(command.to_packet())
            return await self.expect(response_cls, timeout=timeout)

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
        """
        0 (0x00): Ping Command

        The device will return the Ping Command to the host.
        """

        return await self.send_command(
            Ping(payload), Pong, timeout=timeout, retry_times=retry_times
        )

    async def test_connection(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> None:
        """
        Test the connection by sending a ping and checking that the response matches.
        """

        payload: bytes = "".join(
            random.choice(ascii_lowercase) for _ in range(16)
        ).encode("ascii")
        try:
            pong = await self.ping(payload, timeout=timeout, retry_times=retry_times)
        except TimeoutError as exc:
            raise ConnectionError(
                "Failed to receive packet within "
                f"{timeout if timeout is not None else self._default_timeout} seconds"
            ) from exc
        if pong.response != payload:
            raise ConnectionError(f"{pong.response} != {payload}")

    async def detect_baud_rate(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> None:
        """
        Detect the device's configured baud rate by testing the connection at each
        potential baud setting.
        """

        baud_rate = self.baud_rate
        try:
            logger.info(f"Testing connection at {baud_rate} bps...")
            await self.test_connection(timeout, retry_times)
        except ConnectionError as exc:
            logger.debug(exc)
            other_baud_rate = OTHER_BAUD_RATE[baud_rate]
            self.baud_rate = other_baud_rate
            logger.info(
                f"Connection failed at {baud_rate} bps. "
                f"Testing connection at {other_baud_rate} bps..."
            )
            try:
                await self.test_connection(timeout, retry_times)
            except ConnectionError as exc:
                logger.info(
                    f"Connection failed for both {baud_rate} bps "
                    f"and {other_baud_rate} bps."
                )
                raise exc
        else:
            logger.info(f"Connection successful at {baud_rate} bps.")

    async def versions(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Versions:
        """
        1 (0x01): Get Hardware & Firmware Version

        The device will return the hardware and firmware version information to the
        host.
        """

        return await self.send_command(
            GetVersions(), Versions, timeout=timeout, retry_times=retry_times
        )

    async def detect_device(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> None:
        """
        Get model, hardware and firmware versions from the device, then configure the
        client to use that device. This is useful if you don't know a priori what
        device you're using.
        """

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
        """
        2 (0x02): Write User Flash Area

        The CFA533 reserves 16 bytes of nonvolatile memory for arbitrary use by the
        host. This memory can be used to store a serial number, IP address, gateway
        address, netmask, or any other data required. All 16 bytes must be supplied.
        """

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
        """
        3 (0x03): Read User Flash Area

        This command will read the User Flash Area and return the data to the host.
        For more information, review the documentation for
        `client.write_user_flash_area`.
        """

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
        """
        4 (0x04): Store Current State as Boot State

        The device loads its power-up configuration from nonvolatile memory when
        power is applied. The device is configured at the factory to display a
        "welcome" screen when power is applied. This command can be used to customize
        the "welcome" screen, as well as the following items:

        - Characters shown on LCD
        - Special character font definitions
        - Cursor position
        - Cursor style
        - Contrast setting
        - LCD backlight setting
        - Settings of any "live" displays, such as temperature display
        - Key press and release masks
        - ATX function enable and pulse length settings
        - Baud rate
        - GPIO settings

        You cannot store the temperature reporting (although the live display of
        temperatures can be saved). You cannot store the host watchdog. The host
        software should enable this item once the system is initialized and is ready
        to receive the data.
        """

        return await self.send_command(
            StoreBootState(), BootStateStored, timeout=timeout, retry_times=retry_times
        )

    async def reboot_lcd(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> PowerResponse:
        """
        Reboot the device, using 5 (0x05): Reboot Device, Reset Host, or Power Off
        Host.

        Rebooting the device may be useful for testing the boot configuration. It may
        also be useful to re-enumerate the devices on the One-Wire bus.
        """

        return await self.send_command(
            RebootLCD(), PowerResponse, timeout=timeout, retry_times=retry_times
        )

    async def reset_host(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> PowerResponse:
        """
        Reset the host, using 5 (0x05): Reboot Device, Reset Host, or Power Off Host.

        This command assumes the host's reset line is connected to GPIO[3]. For more
        information, review your device's datasheet.
        """

        await self.send_command(ResetHost(), PowerResponse)
        return await self.expect(
            PowerResponse, timeout=timeout, retry_times=retry_times
        )

    async def shutdown_host(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> PowerResponse:
        """
        Turn off the host's power, using 5 (0x05): Reboot Device, Reset Host, or Power
        Off Host.

        This command assumes the host's power control line is connected to GPIO[2].
        For more information, review your device's datasheet.
        """

        return await self.send_command(
            ShutdownHost(), PowerResponse, timeout=timeout, retry_times=retry_times
        )

    async def clear_screen(
        self: Self,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> ClearedScreen:
        """
        6 (0x06): Clear LCD Screen

        Sets the contents of the LCD screen DDRAM to '' = 0x20 = 32 and moves the
        cursor to the left-most column of the top line.
        """

        return await self.send_command(
            ClearScreen(), ClearedScreen, timeout=timeout, retry_times=retry_times
        )

    async def set_line_1(
        self: Self,
        line: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Line1Set:
        """
        7 (0x07): Set LCD Contents, Line 1

        Sets the center 16 characters displayed on the top line of the LCD screen.

        Please use this command only if you need backwards compatibility with older
        devices. For new applications, please use the more flexible command
        `client.send_data`.
        """

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
        """
        8 (0x08): Set LCD Contents, Line 2

        Sets the center 16 characters displayed on the bottom line of the LCD screen.

        Please use this command only if you need backwards compatibility with older
        devices. For new applications, please use the more flexible command
        `client.send_data`.
        """

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
        """
        9 (0x09): Set LCD Special Character Data

        Sets the font definition for one of the special characters (CGRAM).
        """

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
    ) -> None:
        """
        Configure a unicode character to encode to the index of a given special
        character on CGRAM.
        """

        self.device.character_rom.set_encoding(character, index)

    async def read_lcd_memory(
        self: Self,
        address: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> LcdMemory:
        """
        10 (0x0A): Read 8 bytes of LCD Memory

        This command will return the contents of the LCD's DDRAM or CGRAM. This
        command is intended for debugging.
        """

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
        """
        11 (0x0B): Set LCD Cursor Position

        This command allows the cursor to be placed at the desired location on the
        device's LCD screen.
        """

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
        """
        12 (0x0C): Set LCD Cursor Style

        This command allows you to select among four hardware generated cursor
        options.
        """

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
        """
        13 (0x0D): Set LCD Contrast

        This command sets the contrast or vertical viewing angle of the display.
        """

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
        """
        14 (0x0E): Set LCD & Keypad Backlight

        This command sets the brightness of the LCD and keypad backlights.
        """

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
        """
        18 (0x12): Read DOW Device Information

        When power is applied to the unit, it detects any devices connected to the
        Dallas Semiconductor One-Wire (DOW) bus and stores the device's information.
        This command will allow the host to read the device's information.

        Note: The GPIO pin used for DOW must not be configured as user GPIO. For more
        information, review your unit's datasheet.
        """

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
        """
        19 (0x13): Set Up Temperature Reporting

        This command will configure the device to report the temperature information
        to the host every second.
        """

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
        data_to_write: Optional[bytes] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DowTransactionResult:
        """
        20 (0x14): Arbitrary DOW Transaction

        The unit can function as an RS-232 to Dallas 1-Wire bridge. The unit can
        send up to 15 bytes and receive up to 14 bytes. This will be sufficient for
        many devices, but some devices require larger transactions and cannot by fully
        used with the unit.

        For more information, review your unit's datasheet.
        """

        return await self.send_command(
            DowTransaction(
                index,
                bytes_to_read,
                data_to_write if data_to_write is not None else b"",
            ),
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
        """
        21 (0x15): Set Up Live Temperature Display

        You can configure the device to automatically update a portion of the LCD with
        a "live" temperature reading. Once the display is configured using this
        command, the device will continue to display the live reading on the LCD
        without host intervention.
        """

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
        """
        22 (0x16): Send Command Directly to the LCD Controller

        The controller on the CFA533 is HD44780 compatible. Generally, you will not
        need low-level access to the LCD controller but some arcane functions of the
        HD44780 are not exposed by the CFA533's command set. This command allows you
        to access the CFA533's LCD controller directly.
        """

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
        """
        23 (0x17): Configure Key Reporting


        By default, the device reports any key event to the host. This command allows
        the key events to be enabled or disabled on an individual basis.
        """

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
        """
        24 (0x18): Read Keypad, Polled Mode

        In some situations, it may be convenient for the host to poll the device for
        key activity. This command allows the host to detect which keys are currently
        pressed, which keys have been pressed since the last poll, and which keys have
        been released since the last poll.
        """

        return await self.send_command(
            PollKeypad(), KeypadPolled, timeout=timeout, retry_times=retry_times
        )

    async def set_atx_power_switch_functionality(
        self: Self,
        settings: AtxPowerSwitchFunctionalitySettings,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> AtxPowerSwitchFunctionalitySet:
        """
        28 (0x1C): Set ATX Power Switch Functionality

        The combination of this device with the Crystalfontz WR-PWR-Y14 cable can
        be used to replace the function of the power and reset switches in a standard
        ATX-compatible system.

        This functionality comes with a number of caveats. Please review your device's
        datasheet for more information.
        """

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
        """
        29 (0x1D): Enable/Disable and Reset the Watchdog

        Some high-availability systems use hardware watchdog timers to ensure that
        a software or hardware failure does not result in an extended system outage.
        Once the host system has booted, a system monitor program is started. The
        system monitor program would enable the watchdog timer on the device. If the
        system monitor program fails to reset the device's watchdog timer, the device
        will reset the host system.

        The GPIO pins used for ATX control must not be configured as user GPIO. For
        more details, review your device's datasheet.
        """

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
        """
        30 (0x1E): Read Reporting & Status

        This command can be used to verify the current items configured to report to
        the host, as well as some other miscellaneous status information. Please
        note that the information returned is not identical between devices, and may
        in fact vary between firmware versions of the same model. As such, the return
        value of this function is not type-safe.
        """

        res: StatusRead = await self.send_command(
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
        """
        31 (0x1F): Send Data to LCD

        This command allows data to be placed at any position on the LCD.
        """

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
        """
        33 (0x21): Set Baud Rate

        This command will change the device's baud rate. This method sends the baud
        rate command, waits for a positive acknowledgement from the device at the old
        baud rate, and then switches to the new baud rate. The baud rate must be saved
        by a call to `client.store_boot_state` if you want the device to power up at
        the new baud rate.
        """

        res: BaudRateSet = await self.send_command(
            SetBaudRate(baud_rate),
            BaudRateSet,
            timeout=timeout,
            retry_times=retry_times,
        )
        self.baud_rate = baud_rate
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
        """
        34 (0x22): Set or Set and Configure GPIO Pins

        The CFA533 (hardware versions 1.4 and up, firmware versions 1.9 and up) has
        five pins for user-definable general purpose input / output (GPIO). These pins
        are shared with the DOW and ATX functions. Be careful when you configure GPIO
        if you want to use the ATX or DOW at the same time.

        This functionality comes with many caveats. Please review the documentation in
        your device's datasheet.
        """

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
        """
        35 (0x23): Read GPIO Pin Levels and Configuration State

        See method `client.set_gpio` for details on the GPIO architecture.

        This functionality comes with many caveats. Please review the documentation in
        your device's datasheet.
        """

        return await self.send_command(
            ReadGpio(index), GpioRead, timeout=timeout, retry_times=retry_times
        )

    #
    # Report handlers
    #

    async def _handle_report(
        self: Self,
        name: str,
        queue: Receiver[R],
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
        """
        Display a marquee effect on the LCD screen.
        """

        return Marquee(
            client=self,
            row=row,
            text=text,
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
        """
        Display a screensaver effect on the LCD screen.
        """

        return Screensaver(
            client=self,
            text=text,
            tick=tick,
            timeout=timeout,
            retry_times=retry_times,
            loop=self.loop,
        )

    def dance_party(
        self: Self,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DanceParty:
        """
        Display a dance party effect on the LCD screen.
        """

        return DanceParty(
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
    """
    Create a connection to the specified device. Returns a Client object.

    To close the connection, call `client.close()`. The `client.closed` property is a
    Future that will resolve when the client is closed (either due to a call to
    `client.close()` or an error) and should be awaited.
    """

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
async def connection(
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
    """
    Create a connection to the specified device, with an associated context.

    This context will automatically close the connection on exit and wait for the
    connection to close.
    """

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
