import asyncio
from dataclasses import asdict, dataclass, is_dataclass
import functools
import json
import logging
import os
import sys
from typing import (
    Any,
    Callable,
    cast,
    Coroutine,
    Dict,
    List,
    Literal,
    Optional,
    Self,
    Tuple,
    Type,
    TypeVar,
)
import warnings

import click
from serial.serialutil import SerialException

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate, FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.client import (
    Client,
    create_connection,
    DEFAULT_RETRY_TIMES,
    DEFAULT_TIMEOUT,
)
from crystalfontz.config import Config, GLOBAL_FILE
from crystalfontz.cursor import CursorStyle
from crystalfontz.effects import Effect
from crystalfontz.error import CrystalfontzError
from crystalfontz.format import format_json_bytes, OutputMode
from crystalfontz.gpio import GpioDriveMode, GpioFunction, GpioSettings
from crystalfontz.keys import (
    KeyPress,
    KP_DOWN,
    KP_ENTER,
    KP_EXIT,
    KP_LEFT,
    KP_RIGHT,
    KP_UP,
)
from crystalfontz.lcd import LcdRegister
from crystalfontz.report import CliReportHandler, NoopReportHandler, ReportHandler
from crystalfontz.temperature import TemperatureDisplayItem, TemperatureUnit

logger = logging.getLogger(__name__)


@dataclass
class EffectOptions:
    """
    Options for effects.
    """

    tick: Optional[float]
    for_: Optional[float]


@dataclass
class Obj:
    """
    The main click context object. Contains options collated from parameters and the
    loaded config file.
    """

    config: Config
    global_: bool
    port: str
    model: str
    hardware_rev: Optional[str]
    firmware_rev: Optional[str]
    output: OutputMode
    timeout: Optional[float]
    retry_times: Optional[int]
    baud_rate: BaudRate
    effect_options: Optional[EffectOptions] = None


LogLevel = (
    Literal["DEBUG"]
    | Literal["INFO"]
    | Literal["WARNING"]
    | Literal["ERROR"]
    | Literal["CRITICAL"]
)


BYTE_ESCAPE_SEQUENCES: Dict[str, bytes] = {
    "\n": b"",
    "\\": b"\\",
    "'": b"'",
    '"': b'"',
    "a": b"\a",
    "b": b"\b",
    "f": b"\f",
    "n": b"\n",
    "r": b"\r",
    "\t": b"\t",
    "\v": b"\v",
}

BYTE_VALUE_ESCAPE_SEQUENCES: Dict[str, Tuple[List[int], int]] = {
    "o": ([3, 2], 8),
    "x": ([2], 16),
}


def parse_bytes(text: str) -> bytes:
    """
    Parse a string representation of bytes into bytes. Supports the same escape
    sequences as Python's bytes literals.
    """

    buffer: bytes = b""

    i = 0

    WARNING_MESSAGE = "invalid escape sequence '{}'"

    def invalid(seq: str) -> None:
        nonlocal i
        nonlocal buffer
        buffer = buffer + seq.encode("utf-8")
        i += len(seq)

    def parse_escape_sequence() -> None:
        nonlocal i
        nonlocal buffer
        widths, radix = BYTE_VALUE_ESCAPE_SEQUENCES[text[i + 1]]

        # Some escape sequences support different skip lengths. These skip
        # lengths are sorted in reverse order
        min_width = widths[-1]
        min_end = i + 2 + min_width

        # If the string is shorter than the min skip, warn and return
        if min_end > len(text):
            warnings.warn(WARNING_MESSAGE.format(text[i:]), SyntaxWarning)
            invalid(text[i:])
            return

        for width in widths:
            start = i + 2
            end = i + 2 + width
            try:
                code = int(text[start:end], radix)
                buffer += code.to_bytes(1, "big")
            except ValueError as exc:
                # Digits weren't valid
                if width > min_width:
                    # There are other widths to try
                    logger.debug(exc)
                    continue
                # No widths are shorter!
                logger.warning(exc)
                warnings.warn(WARNING_MESSAGE.format(text[i:end]), SyntaxWarning)
                invalid(text[i:end])
                return
            else:
                i = end
                return
        raise CrystalfontzError("assert: unreachable")

    while i < len(text):
        if text[i] == "\\":
            if (i + 1) >= len(text):
                # Last character in text is \
                warnings.warn(WARNING_MESSAGE.format("\\"), SyntaxWarning)
                invalid("\\")
                continue
            if text[i + 1] in BYTE_ESCAPE_SEQUENCES:
                buffer += BYTE_ESCAPE_SEQUENCES[text[i + 1]]
                i += 2
                continue
            elif text[i + 1] in BYTE_VALUE_ESCAPE_SEQUENCES:
                parse_escape_sequence()
                continue
            else:
                warnings.warn(WARNING_MESSAGE.format(text[i : i + 1]), SyntaxWarning)
                invalid(text[i : i + 1])
                continue
        buffer += text[i : i + 1].encode("utf-8")
        i += 1

    return buffer


class Bytes(click.ParamType):
    """
    A parameter containing byte escape codes.
    """

    name = "bytes"

    def convert(
        self: Self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> bytes:
        try:
            return parse_bytes(value)
        except Exception as exc:
            self.fail(f"{value!r} is not valid bytes: {exc}", param, ctx)


class Byte(click.IntRange):
    """
    A parameter representing a single byte - an integer in [0, 255].
    """

    name = "byte"

    def __init__(self: Self) -> None:
        super().__init__(min=0, max=255)


class WatchdogSetting(Byte):
    """
    A watchdog setting. This is typically an integer, but the values "disable" and
    "disabled" are supported as aliases for 0.
    """

    name = "watchdog_setting"

    def convert(
        self: Self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> int:
        if value == "disable" or value == "disabled":
            return 0
        return super().convert(value, param, ctx)


class BaudRateParam(click.INT.__class__):
    name = "baud_rate"

    def convert(
        self: Self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> BaudRate:
        rate = super().convert(value, param, ctx)
        if rate == SLOW_BAUD_RATE or rate == FAST_BAUD_RATE:
            return rate
        self.fail(f"Baud rate {rate} is unsupported", param, ctx)


class Function(click.Choice):
    """
    A GPIO function parameter. Either used or unused.
    """

    name = "function"

    def __init__(self: Self) -> None:
        super().__init__(["used", "unused", "USED", "UNUSED"])

    def convert(
        self: Self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> GpioFunction:
        choice = super().convert(value, param, ctx)

        if choice in {"used", "USED"}:
            return GpioFunction.USED
        else:
            return GpioFunction.UNUSED


class DriveMode(click.Choice):
    """
    A GPIO drive mode. Each direction supports one of four settings, which are
    in turn supported in various combinations.
    """

    name = "drive_mode"

    def __init__(self: Self) -> None:
        super().__init__(["slow-strong", "fast-strong", "resistive", "hi-z"])

    def convert(
        self: Self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> GpioDriveMode:
        choice = super().convert(value, param, ctx)
        if choice == "slow-strong":
            return GpioDriveMode.SLOW_STRONG
        elif choice == "fast-strong":
            return GpioDriveMode.FAST_STRONG
        elif choice == "resistive":
            return GpioDriveMode.RESISTIVE
        else:
            return GpioDriveMode.HI_Z


BYTES = Bytes()
BYTE = Byte()
WATCHDOG_SETTING = WatchdogSetting()
BAUD_RATE = BaudRateParam()
FUNCTION = Function()
DRIVE_MODE = DriveMode()


def as_json(obj: Any) -> Any:
    """
    Convert an object into something that is JSON-serializable.
    """
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    elif is_dataclass(obj.__class__):
        return asdict(obj)
    elif isinstance(obj, bytes):
        return format_json_bytes(obj)
    else:
        return obj


class Echo:
    """
    An abstraction for writing output to the terminal. Used to support the
    behavior of the --output flag.
    """

    mode: OutputMode = "text"

    def __call__(self: Self, obj: Any, *args, **kwargs) -> None:
        if self.mode == "json":
            try:
                click.echo(json.dumps(as_json(obj), indent=2), *args, **kwargs)
            except Exception as exc:
                logger.debug(exc)
                click.echo(json.dumps(repr(obj)), *args, **kwargs)
        else:
            click.echo(
                obj if isinstance(obj, bytes) or isinstance(obj, str) else repr(obj),
                *args,
                **kwargs,
            )


echo = Echo()

AsyncCommand = Callable[..., Coroutine[None, None, None]]
SyncCommand = Callable[..., None]


def async_command(fn: AsyncCommand) -> SyncCommand:
    """
    Run an async command handler.
    """

    @functools.wraps(fn)
    def wrapped(*args, **kwargs) -> None:
        try:
            asyncio.run(fn(*args, **kwargs))
        except KeyboardInterrupt:
            pass

    return wrapped


def pass_client(
    run_forever: bool = False,
    report_handler_cls: Type[ReportHandler] = NoopReportHandler,
) -> Callable[[AsyncCommand], AsyncCommand]:
    def decorator(fn: AsyncCommand) -> AsyncCommand:
        @click.pass_obj
        @functools.wraps(fn)
        async def wrapped(obj: Obj, *args, **kwargs) -> None:
            port: str = obj.port
            model = obj.model
            hardware_rev = obj.hardware_rev
            firmware_rev = obj.firmware_rev
            output = obj.output
            timeout = obj.timeout
            retry_times = obj.retry_times
            baud_rate: BaudRate = obj.baud_rate

            report_handler = report_handler_cls()

            # Set the output mode on the report handler
            if isinstance(report_handler, CliReportHandler):
                report_handler.mode = output

            # Set the output mode for echo
            echo.mode = output

            to: float = timeout if timeout is not None else DEFAULT_TIMEOUT
            retries: int = (
                retry_times if retry_times is not None else DEFAULT_RETRY_TIMES
            )

            try:
                client: Client = await create_connection(
                    port,
                    model=model,
                    hardware_rev=hardware_rev,
                    firmware_rev=firmware_rev,
                    report_handler=report_handler,
                    timeout=to,
                    retry_times=retries,
                    baud_rate=baud_rate,
                )
            except SerialException as exc:
                click.echo(exc)
                sys.exit(1)

            try:
                # Giddyup!
                await fn(client, *args, **kwargs)
            except TimeoutError:
                logger.error(
                    f"Command timed out after {to} seconds and {retries} retries."
                )

            # Close the client if we're done
            if not run_forever:
                client.close()

            # Await the client closing and surface any exceptions
            await client.closed

        return wrapped

    return decorator


R = TypeVar("R")


def pass_config(fn: Callable[..., R]) -> Callable[..., R]:
    @click.pass_obj
    @functools.wraps(fn)
    def wrapped(obj: Obj, *args, **kwargs) -> R:
        return fn(obj.config, *args, **kwargs)

    return wrapped


@click.group()
@click.option(
    "--global/--no-global",
    "global_",
    default=os.geteuid() == 0,
    help=f"Load the global config file at {GLOBAL_FILE} "
    "(default true when called with sudo)",
)
@click.option(
    "--config-file",
    "-C",
    envvar="CRYSTALFONTZ_CONFIG_FILE",
    type=click.Path(),
    help="A path to a config file",
)
@click.option(
    "--log-level",
    envvar="CRYSTALFONTZ_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Set the log level",
)
@click.option(
    "--port",
    envvar="CRYSTALFONTZ_PORT",
    help="The serial port the device is connected to",
)
@click.option(
    "--model",
    envvar="CRYSTALFONTZ_MODEL",
    help="The model of the device",
    type=click.Choice(["CFA533", "CFA633"]),
    default="CFA533",
)
@click.option(
    "--hardware-rev",
    envvar="CRYSTALFONTZ_HARDWARE_REV",
    help="The hardware revision of the device",
)
@click.option(
    "--firmware-rev",
    envvar="CRYSTALFONTZ_FIRMWARE_REV",
    help="The firmware revision of the device",
)
@click.option(
    "--output",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output either human-friendly text or JSON",
)
@click.option(
    "--timeout",
    type=float,
    envvar="CRYSTALFONTZ_TIMEOUT",
    help="How long to wait for a response from the device before timing out",
)
@click.option(
    "--retry-times",
    type=int,
    envvar="CRYSTALFONTZ_RETRY_TIMES",
    help="How many times to retry a command if a response times out",
)
@click.option(
    "--baud",
    type=click.Choice([str(SLOW_BAUD_RATE), str(FAST_BAUD_RATE)]),
    envvar="CRYSTALFONTZ_BAUD_RATE",
    help="The baud rate to use when connecting to the device",
)
@click.pass_context
def main(
    ctx: click.Context,
    global_: bool,
    config_file: Optional[str],
    log_level: LogLevel,
    port: Optional[str],
    model: str,
    hardware_rev: Optional[str],
    firmware_rev: Optional[str],
    output: Optional[OutputMode],
    timeout: Optional[float],
    retry_times: Optional[int],
    baud: Optional[str],
) -> None:
    """
    Control your Crystalfontz device.
    """

    baud_rate = cast(Optional[BaudRate], int(baud) if baud else None)
    file = None
    if config_file:
        if global_:
            warnings.warn(
                "--config-file is specified, so --global flag will be ignored."
            )
        file = config_file
    elif global_:
        file = GLOBAL_FILE
    config: Config = Config.from_file(file=file)
    ctx.obj = Obj(
        config=config,
        global_=global_,
        port=port or config.port,
        model=model or config.model,
        hardware_rev=hardware_rev or config.hardware_rev,
        firmware_rev=firmware_rev or config.firmware_rev,
        output=output or "text",
        timeout=timeout or config.timeout,
        retry_times=retry_times if retry_times is not None else config.retry_times,
        baud_rate=baud_rate or config.baud_rate,
    )

    logging.basicConfig(level=getattr(logging, log_level))


@main.group()
def config() -> None:
    """
    Configure crystalfontz.
    """
    pass


@config.command()
@click.argument("name")
@pass_config
def get(config: Config, name: str) -> None:
    """
    Get a parameter from the configuration file.
    """

    try:
        echo(config.get(name))
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)


@config.command()
@pass_config
def show(config: Config) -> None:
    """
    Show the current configuration.
    """
    echo(config)


@config.command()
@click.argument("name")
@click.argument("value")
@pass_config
def set(config: Config, name: str, value: str) -> None:
    """
    Set a parameter in the configuration file.
    """
    try:
        config.set(name, value)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    config.to_file()


@config.command()
@click.argument("name")
@pass_config
def unset(config: Config, name: str) -> None:
    """
    Unset a parameter in the configuration file.
    """
    try:
        config.unset(name)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    config.to_file()


@config.command()
@click.option("--baud/--no-baud", default=True, help="Detect baud rate")
@click.option(
    "--device/--no-device", default=True, help="Detect device model and versions"
)
@click.option(
    "--save/--no-save", default=True, help="Whether or not to save the configuration"
)
@async_command
@pass_client()
@pass_config
async def detect(
    config: Config, client: Client, baud: bool, device: bool, save: bool
) -> None:
    """
    Detect device versions and baud rate.
    """

    if baud:
        try:
            await client.detect_baud_rate()
        except ConnectionError as exc:
            logger.debug(exc)
            sys.exit(1)
        else:
            config.baud_rate = client.baud_rate

    if device:
        await client.detect_device()

        config.model = client.model
        config.hardware_rev = client.hardware_rev
        config.firmware_rev = client.firmware_rev

    if save:
        config.to_file()
    else:
        echo(config)


@main.command()
@click.option("--for", "for_", type=float, help="Amount of time to listen for reports")
@async_command
@pass_client(run_forever=True, report_handler_cls=CliReportHandler)
async def listen(client: Client, for_: Optional[float]) -> None:
    """
    Listen for key activity and temperature reports.

    To configure which reports to receive, use
    'python -m crystalfontz keypad reporting' and
    'python -m crystalfontz temperature reporting' respectively.
    """

    if for_ is not None:
        await asyncio.sleep(for_)
        client.close()


@main.command(help="0 (0x00): Ping command")
@click.argument("payload", type=BYTES)
@async_command
@pass_client()
async def ping(client: Client, payload: bytes) -> None:
    pong = await client.ping(payload)
    echo(pong.response)


@main.command(help="1 (0x01): Get Hardware & Firmware Version")
@async_command
@pass_client()
async def versions(client: Client) -> None:
    versions = await client.versions()
    echo(versions)


@main.group(help="Interact with the User Flash Area")
def flash() -> None:
    pass


@flash.command(name="write", help="2 (0x02): Write User Flash Area")
@click.argument("data", type=BYTES)
@async_command
@pass_client()
async def write_user_flash_area(client: Client, data: bytes) -> None:
    await client.write_user_flash_area(data)


@flash.command(name="read", help="3 (0x03): Read User Flash Area")
@async_command
@pass_client()
async def read_user_flash_area(client: Client) -> None:
    flash = await client.read_user_flash_area()
    echo(flash.data)


@main.command(help="4 (0x04): Store Current State as Boot State")
@async_command
@pass_client()
async def store(client: Client) -> None:
    await client.store_boot_state()


@main.group(help="5 (0x05): Reboot LCD, Reset Host, or Power Off Host")
def power() -> None:
    pass


@power.command(help="Reboot the Crystalfontx LCD")
@async_command
@pass_client()
async def reboot_lcd(client: Client) -> None:
    await client.reboot_lcd()


@power.command(help="Reset the host, assuming ATX control is configured")
@async_command
@pass_client()
async def reset_host(client: Client) -> None:
    await client.reset_host()


@power.command(help="Turn the host's power off, assuming ATX control is configured")
@async_command
@pass_client()
async def shutdown_host(client: Client) -> None:
    await client.shutdown_host()


@main.command(help="6 (0x06): Clear LCD Screen")
@async_command
@pass_client()
async def clear(client: Client) -> None:
    await client.clear_screen()


@main.group(help="Set LCD contents for a line")
def line() -> None:
    pass


@line.command(name="1", help="7 (0x07): Set LCD Contents, Line 1")
@click.argument("line", type=BYTES)
@async_command
@pass_client()
async def set_line_1(client: Client, line: bytes) -> None:
    await client.set_line_1(line)


@line.command(name="2", help="8 (0x08): Set LCD Contents, Line 2")
@click.argument("line", type=BYTES)
@async_command
@pass_client()
async def set_line_2(client: Client, line: bytes) -> None:
    await client.set_line_2(line)


@main.command(help="Interact with special characters")
def character() -> None:
    #
    # Two functions are intended to be implemented under this namespace, both of which
    # have missing semantics:
    #
    # 1. 9 (0x09): Set LCD Special Character Data. Special characters don't
    #    currently have good support for loading pixels from files - text or
    #    otherwise.
    # 2. Configuring encoding for using special characters. This would need
    #    to be stateful to be useful, meaning the config file would likely
    #    need to support it in some capacity.
    #
    raise NotImplementedError("character")


@main.group(help="Interact directly with the LCD controller")
def lcd() -> None:
    pass


@lcd.command(name="poke", help="10 (0x0A): Read 8 Bytes of LCD Memory")
@click.argument("address", type=BYTE)
@async_command
@pass_client()
async def read_lcd_memory(client: Client, address: int) -> None:
    memory = await client.read_lcd_memory(address)
    echo(memory)


@main.group(help="Interact with the LCD cursor")
def cursor() -> None:
    pass


@cursor.command(name="position", help="11 (0x0B): Set LCD Cursor Position")
@click.argument("row", type=BYTE)
@click.argument("column", type=BYTE)
@async_command
@pass_client()
async def set_cursor_position(client: Client, row: int, column: int) -> None:
    await client.set_cursor_position(row, column)


@cursor.command(name="style", help="12 (0x0C): Set LCD Cursor Style")
@click.argument("style", type=click.Choice([e.name for e in CursorStyle]))
@async_command
@pass_client()
async def set_cursor_style(client: Client, style: str) -> None:
    await client.set_cursor_style(CursorStyle[style])


@main.command(help="13 (0x0D): Set LCD Contrast")
@click.argument("contrast", type=float)
@async_command
@pass_client()
async def contrast(client: Client, contrast: float) -> None:
    await client.set_contrast(contrast)


@main.command(help="14 (0x0E): Set LCD & Keypad Backlight")
@click.argument("brightness", type=float)
@click.option("--keypad", type=float)
@async_command
@pass_client()
async def backlight(client: Client, brightness: float, keypad: Optional[float]) -> None:
    await client.set_backlight(brightness, keypad)


@main.group(help="DOW (Dallas One-Wire) capabilities")
def dow() -> None:
    pass


@dow.command(name="info", help="18 (0x12): Read DOW Device Information")
@click.argument("index", type=BYTE)
@async_command
@pass_client()
async def read_dow_device_information(client: Client, index: int) -> None:
    info = await client.read_dow_device_information(index)
    echo(info)


@main.group(help="Temperature reporting and live display")
def temperature() -> None:
    pass


@temperature.command(name="reporting", help="19 (0x13): Set Up Temperature Reporting")
@click.argument("enabled", nargs=-1)
@async_command
@pass_client()
async def setup_temperature_reporting(client: Client, enabled: Tuple[int, ...]) -> None:
    await client.setup_temperature_reporting(enabled)


@dow.command(name="transaction", help="20 (0x14): Arbitrary DOW Transaction")
@click.argument("index", type=BYTE)
@click.argument("bytes_to_read", type=BYTE)
@click.option("--data_to_write", type=BYTES)
@async_command
@pass_client()
async def dow_transaction(
    client: Client, index: int, bytes_to_read: int, data_to_write: Optional[bytes]
) -> None:
    res = await client.dow_transaction(index, bytes_to_read, data_to_write)
    echo(res)


@temperature.command(name="display", help="21 (0x15): Set Up Live Temperature Display")
@click.argument("slot", type=BYTE)
@click.argument("index", type=BYTE)
@click.option("--n-digits", "-n", type=click.Choice(["3", "5"]), required=True)
@click.option("--column", "-c", type=BYTE, required=True)
@click.option("--row", "-r", type=BYTE, required=True)
@click.option("--units", "-U", type=click.Choice([e.name for e in TemperatureUnit]))
@async_command
@pass_client()
async def setup_live_temperature_display(
    client: Client,
    slot: int,
    index: int,
    n_digits: str,
    column: int,
    row: int,
    units: str,
) -> None:
    await client.setup_live_temperature_display(
        slot,
        TemperatureDisplayItem(
            index=index,
            n_digits=cast(Any, int(n_digits)),
            column=column,
            row=row,
            units=TemperatureUnit[units],
        ),
    )


@lcd.command(name="send", help="22 (0x16): Send Command Directly to the LCD Controller")
@click.argument("location", type=click.Choice([e.name for e in LcdRegister]))
@click.argument("data", type=BYTE)
@async_command
@pass_client()
async def send_command_to_lcd_controler(
    client: Client, location: str, data: int
) -> None:
    await client.send_command_to_lcd_controller(LcdRegister[location], data)


@main.group(help="Interact with the keypad")
def keypad() -> None:
    pass


KEYPRESSES: Dict[str, int] = dict(
    KP_UP=KP_UP,
    KP_ENTER=KP_ENTER,
    KP_EXIT=KP_EXIT,
    KP_LEFT=KP_LEFT,
    KP_RIGHT=KP_RIGHT,
    KP_DOWN=KP_DOWN,
)


@keypad.command(name="reporting", help="23 (0x17): Configure Key Reporting")
@click.option(
    "--when-pressed", multiple=True, type=click.Choice(list(KEYPRESSES.keys()))
)
@click.option(
    "--when-released", multiple=True, type=click.Choice(list(KEYPRESSES.keys()))
)
@async_command
@pass_client()
async def configure_key_reporting(
    client: Client, when_pressed: List[str], when_released: List[str]
) -> None:
    await client.configure_key_reporting(
        when_pressed={cast(KeyPress, KEYPRESSES[name]) for name in when_pressed},
        when_released={cast(KeyPress, KEYPRESSES[name]) for name in when_released},
    )


@keypad.command(name="poll", help="24 (0x18): Read Keypad, Polled Mode")
@async_command
@pass_client()
async def poll_keypad(client: Client) -> None:
    polled = await client.poll_keypad()
    echo(polled)


@main.command(help="28 (0x1C): Set ATX Power Switch Functionality")
@click.argument(
    "function", nargs=-1, type=click.Choice([e.name for e in AtxPowerSwitchFunction])
)
@click.option(
    "--auto-polarity/--no-auto-polarity",
    type=bool,
    default=False,
    help="Whether or not to automatically detect polarity for reset and power",
)
@click.option(
    "--power-pulse-length",
    type=float,
    help="Length of power on and off pulses in seconds",
)
@async_command
@pass_client()
async def atx(
    client: Client,
    function: List[str],
    auto_polarity: bool,
    power_pulse_length: Optional[float],
) -> None:
    await client.set_atx_power_switch_functionality(
        AtxPowerSwitchFunctionalitySettings(
            functions={AtxPowerSwitchFunction[name] for name in function},
            auto_polarity=auto_polarity,
            power_pulse_length_seconds=power_pulse_length,
        )
    )


@main.command(help="29 (0x1D): Enable/Disable and Reset the Watchdog")
@click.argument("timeout_seconds", type=WATCHDOG_SETTING)
@async_command
@pass_client()
async def watchdog(client: Client, timeout_seconds: int) -> None:
    await client.configure_watchdog(timeout_seconds)


@main.command(help="30 (0x1E): Read Reporting & Status")
@async_command
@pass_client()
async def status(client: Client) -> None:
    status = await client.read_status()

    echo(status)


@main.command(help="31 (0x1F): Send Data to LCD")
@click.argument("row", type=int)
@click.argument("column", type=int)
@click.argument("data", type=BYTES)
@async_command
@pass_client()
async def send(client: Client, row: int, column: int, data: bytes) -> None:
    await client.send_data(row, column, data)


@main.command(help="33 (0x21): Set Baud Rate")
@click.argument("rate", type=BAUD_RATE)
@click.option(
    "--save/--no-save",
    default=False,
    help="Save the new baud rate to the configuration",
)
@click.pass_obj
@async_command
@pass_client()
async def baud(client: Client, obj: Obj, rate: BaudRate, save: bool) -> None:
    await client.set_baud_rate(rate)

    if save:
        config = obj.config
        config.baud_rate = client.baud_rate
        logger.info(f"Saving baud rate {client.baud_rate} to {config.file}")
        obj.config = config.to_file()


@main.group(help="Interact with GPIO pins")
def gpio() -> None:
    pass


def load_gpio_settings(
    function: Optional[GpioFunction],
    up: Optional[GpioDriveMode],
    down: Optional[GpioDriveMode],
) -> Optional[GpioSettings]:
    settings: Optional[GpioSettings] = None
    settings_undefined = function is None and up is None and down is None
    if not settings_undefined:
        if not function:
            raise ValueError("When configuring GPIO pins, a function must be defined")
        if not up:
            raise ValueError(
                "When configuring GPIO pins, a pull-up mode must be defined"
            )
        if not down:
            raise ValueError(
                "When configuring GPIO pins, a pull-down mode must be defined"
            )
        settings = GpioSettings(function=function, up=up, down=down)
    return settings


@gpio.command(name="set", help="34 (0x22): Set or Set and Configure GPIO Pins")
@click.argument("index", type=BYTE)
@click.argument("state", type=BYTE)
@click.option("--function", type=FUNCTION, help="The GPIO pin's function")
@click.option("--up", type=DRIVE_MODE, help="The GPIO pin's pull-up drive mode")
@click.option("--down", type=DRIVE_MODE, help="The GPIO pin's pull-down drive mode")
@async_command
@pass_client()
async def set_gpio(
    client: Client,
    index: int,
    output_state: int,
    function: Optional[GpioFunction],
    up: Optional[GpioDriveMode],
    down: Optional[GpioDriveMode],
) -> None:
    settings = load_gpio_settings(function, up, down)
    await client.set_gpio(index, output_state, settings)


@gpio.command(
    name="read", help="35 (0x23): Read GPIO Pin Levels and Configuration State"
)
@click.argument("index", type=BYTE)
@async_command
@pass_client()
async def read_gpio(client: Client, index: int) -> None:
    res = await client.read_gpio(index)
    echo(res)


@main.group(help="Run various effects, such as marquees")
@click.option("--tick", type=float, help="How often to update the effect")
@click.option("--for", "for_", type=float, help="Amount of time to run the effect for")
@click.pass_obj
def effects(obj: Obj, tick: Optional[float], for_: Optional[float]) -> None:
    obj.effect_options = EffectOptions(tick=tick, for_=for_)


async def run_effect(
    effect: Effect, loop: asyncio.AbstractEventLoop, for_: Optional[float]
) -> None:
    f = loop.create_task(effect.run())
    if for_ is not None:
        await asyncio.sleep(for_)
        effect.stop()

    await f


@effects.command(help="Display a marquee effect")
@click.argument("row", type=int)
@click.argument("text")
@click.option(
    "--pause", type=float, help="An amount of time to pause before starting the effect"
)
@async_command
@pass_client()
@click.pass_obj
async def marquee(
    obj: Obj, client: Client, row: int, text: str, pause: Optional[float]
) -> None:
    tick = obj.effect_options.tick if obj.effect_options else None
    for_ = obj.effect_options.for_ if obj.effect_options else None

    m = client.marquee(row, text, pause=pause, tick=tick)

    await client.clear_screen()

    await run_effect(m, client.loop, for_)


@effects.command(help="Display a screensaver-like effect")
@click.argument("text")
@async_command
@pass_client()
@click.pass_obj
async def screensaver(obj: Obj, client: Client, text: str) -> None:
    tick = obj.effect_options.tick if obj.effect_options else None
    for_ = obj.effect_options.for_ if obj.effect_options else None
    s = client.screensaver(text, tick=tick)

    await run_effect(s, client.loop, for_)


@effects.command(help="Have a dance party!")
@async_command
@pass_client()
@click.pass_obj
async def dance_party(obj: Obj, client: Client) -> None:
    tick = obj.effect_options.tick if obj.effect_options else None
    for_ = obj.effect_options.for_ if obj.effect_options else None
    s = client.dance_party(tick=tick)

    await run_effect(s, client.loop, for_)


if __name__ == "__main__":
    main()
