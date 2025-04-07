import asyncio
from dataclasses import dataclass
import functools
import logging
import os
import shlex
import shutil
import subprocess
import sys
from typing import cast, List, Optional, Tuple

import click

from crystalfontz.atx import AtxPowerSwitchFunction
from crystalfontz.baud import BaudRate
from crystalfontz.cli import (
    async_command,
    AsyncCommand,
    BAUD_RATE,
    BYTE,
    BYTES,
    CursorStyle,
    DRIVE_MODE,
    echo,
    EffectOptions,
    FUNCTION,
    KEYPRESSES,
    load_gpio_settings,
    LogLevel,
    OutputMode,
    run_effect,
    WATCHDOG_SETTING,
)
from crystalfontz.dbus.client import DbusClient
from crystalfontz.dbus.config import StagedConfig
from crystalfontz.dbus.domain import (
    CursorStyleM,
    DeviceStatusM,
    DowDeviceInformationM,
    DowTransactionResultM,
    GpioReadM,
    KeypadBrightnessM,
    KeypadPolledM,
    LcdMemoryM,
    LcdRegisterM,
    OptBytesM,
    OptGpioSettingsM,
    RetryTimesM,
    RetryTimesT,
    TemperatureDisplayItemM,
    TimeoutM,
    TimeoutT,
    VersionsM,
)
from crystalfontz.dbus.effects import DbusEffectClient
from crystalfontz.dbus.error import handle_dbus_error
from crystalfontz.dbus.report import DbusClientCliReportHandler
from crystalfontz.dbus.select import (
    select_default_bus,
    select_session_bus,
    select_system_bus,
)
from crystalfontz.effects import DanceParty, Marquee, Screensaver
from crystalfontz.gpio import GpioDriveMode, GpioFunction
from crystalfontz.lcd import LcdRegister
from crystalfontz.temperature import (
    TemperatureDigits,
    TemperatureDisplayItem,
    TemperatureUnit,
)

logger = logging.getLogger(__name__)


@dataclass
class Obj:
    client: DbusClient
    log_level: LogLevel
    output: OutputMode
    timeout: TimeoutT
    retry_times: RetryTimesT
    report_handler: DbusClientCliReportHandler
    effect_options: Optional[EffectOptions] = None


def pass_config(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        config = await obj.client.staged_config()
        await fn(config, *args, **kwargs)

    return wrapped


def pass_timeout_retry(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        await fn(*args, **kwargs, timeout=obj.timeout, retry_times=obj.retry_times)

    return wrapped


def pass_client(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        async with handle_dbus_error(logger):
            await fn(obj.client, *args, **kwargs)

    return wrapped


def pass_report_handler(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        await fn(obj.report_handler, *args, **kwargs)

    return wrapped


def should_sudo(config_file: str) -> bool:
    st = os.stat(config_file)
    return os.geteuid() != st.st_uid


def run_config_command(obj: Obj, staged: StagedConfig, argv: List[str]) -> None:
    args: List[str] = [
        sys.executable,
        "-m",
        "crystalfontz",
        "--config-file",
        staged.file,
        "--log-level",
        obj.log_level,
        "--output",
        obj.output,
        "config",
    ] + argv

    if should_sudo(staged.file):
        args.insert(0, "sudo")

    try:
        logger.debug(f"Running command: {shlex.join(args)}")
        subprocess.run(args, capture_output=False, check=True)
    except subprocess.CalledProcessError as exc:
        logger.debug(exc)
        sys.exit(exc.returncode)


def warn_dirty() -> None:
    msg = "The service configuration is out of sync. "

    if shutil.which("systemctl"):
        msg += """To reload the service, run:

    sudo system ctl restart crystalfontz"""
    else:
        msg += (
            "To update the configuration, reload the service with your OS's "
            "init system."
        )

    logger.warn(msg)


@click.group()
@click.option(
    "--log-level",
    envvar="CRYSTALFONTZ_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Set the log level",
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
    "--user/--default",
    type=click.BOOL,
    default=None,
    help="Connect to either the user or default bus",
)
@click.pass_context
def main(
    ctx: click.Context,
    log_level: LogLevel,
    output: OutputMode,
    timeout: Optional[float],
    retry_times: Optional[int],
    user: Optional[bool],
) -> None:
    """
    Control your Crystalfontz device.
    """

    logging.basicConfig(level=getattr(logging, log_level))

    # Set the output mode for echo
    echo.mode = output

    async def load() -> None:
        if user:
            select_session_bus()
        elif user is None:
            select_system_bus()
        else:
            select_default_bus()

        report_handler = DbusClientCliReportHandler()
        report_handler.mode = output

        client = DbusClient(report_handler=report_handler)
        ctx.obj = Obj(
            client=client,
            log_level=log_level,
            output=output,
            timeout=TimeoutM.pack(timeout),
            retry_times=RetryTimesM.pack(retry_times),
            report_handler=report_handler,
        )

    asyncio.run(load())


@main.group()
def config() -> None:
    """
    Configure crystalfontz.
    """
    pass


@config.command()
@click.argument("name")
@async_command
@pass_config
async def get(staged: StagedConfig, name: str) -> None:
    """
    Get a parameter from the configuration file.
    """

    try:
        echo(staged.get(name))
    except ValueError as exc:
        echo(str(exc))
        raise SystemExit(1)
    finally:
        if staged.dirty:
            warn_dirty()


@config.command()
@async_command
@pass_config
async def show(staged: StagedConfig) -> None:
    """
    Show the current configuration.
    """
    echo(staged)

    if staged.dirty:
        warn_dirty()


@config.command()
@click.argument("name")
@click.argument("value")
@async_command
@pass_config
@click.pass_obj
async def set(obj: Obj, staged: StagedConfig, name: str, value: str) -> None:
    """
    Set a parameter in the configuration file.
    """

    try:
        run_config_command(obj, staged, ["set", name, value])
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    else:
        staged.reload_target()
    finally:
        if staged.dirty:
            warn_dirty()


@config.command()
@click.argument("name")
@async_command
@pass_config
async def unset(staged: StagedConfig, name: str) -> None:
    """
    Unset a parameter in the configuration file.
    """
    try:
        staged.unset(name)
    except ValueError as exc:
        echo(str(exc))
        sys.exit(1)
    else:
        staged.to_file()
    finally:
        if staged.dirty:
            warn_dirty()


@config.command()
@click.option("--baud/--no-baud", default=True, help="Detect baud rate")
@click.option(
    "--device/--no-device", default=True, help="Detect device model and versions"
)
@click.option(
    "--save/--no-save", default=True, help="Whether or not to save the configuration"
)
@async_command
@pass_client
@pass_config
@click.pass_obj
async def detect(
    obj: Obj,
    staged: StagedConfig,
    client: DbusClient,
    baud: bool,
    device: bool,
    save: bool,
) -> None:
    """
    Detect device versions and baud rate.
    """

    baud_rate = -1
    model = "<unknown>"
    hardware_rev = "<unknown>"
    firmware_rev = "<unknown>"

    if baud:
        baud_rate = await client.detect_baud_rate(obj.timeout, RetryTimesM.none)

    if device:
        device_t = await client.detect_device(obj.retry_times, RetryTimesM.none)
        model = device_t[0]
        hardware_rev = device_t[1]
        firmware_rev = device_t[2]

    if save:
        try:
            run_config_command(obj, staged, ["set", "baud_rate", str(baud_rate)])
            run_config_command(obj, staged, ["set", "model", model])
            run_config_command(obj, staged, ["set", "hardware_rev", hardware_rev])
            run_config_command(obj, staged, ["set", "firmware_rev", firmware_rev])
        except ValueError as exc:
            echo(str(exc))
            sys.exit(1)
        else:
            staged.reload_target()
        finally:
            if staged.dirty:
                warn_dirty()


@main.command()
@click.option("--for", "for_", type=float, help="Amount of time to listen for reports")
@async_command
@pass_report_handler
@pass_client
async def listen(
    client: DbusClient,
    report_handler: DbusClientCliReportHandler,
    for_: Optional[float],
) -> None:
    """
    Listen for key and temperature reports.

    To configure which reports to receive, use 'crystalfontz keypad reporting' and
    'crystalfontz temperature reporting' respectively.
    """

    await report_handler.listen()

    if for_ is not None:
        await asyncio.sleep(for_)
        report_handler.stop()
    await report_handler.done


@main.command(help="0 (0x00): Ping command")
@click.argument("payload", type=BYTES)
@async_command
@pass_timeout_retry
@pass_client
async def ping(
    client: DbusClient, payload: bytes, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    pong = await client.ping(payload, timeout, retry_times)
    echo(pong)


@main.command(help="1 (0x01): Get Hardware & Firmware Version")
@async_command
@pass_timeout_retry
@pass_client
async def versions(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    versions = await client.versions(timeout, retry_times)
    echo(VersionsM.unpack(versions))


@main.group(help="Interact with the User Flash Area")
def flash() -> None:
    pass


@flash.command(name="write", help="2 (0x02): Write User Flash Area")
@click.argument("data", type=BYTES)
@async_command
@pass_timeout_retry
@pass_client
async def write_user_flash_area(
    client: DbusClient, data: bytes, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.write_user_flash_area(data, timeout, retry_times)


@flash.command(name="read", help="3 (0x03): Read User Flash Area")
@async_command
@pass_timeout_retry
@pass_client
async def read_user_flash_area(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    flash = await client.read_user_flash_area(timeout, retry_times)
    echo(flash)


@main.command(help="4 (0x04): Store Current State as Boot State")
@async_command
@pass_timeout_retry
@pass_client
async def store(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.store_boot_state(timeout, retry_times)


@main.group(help="5 (0x05): Reboot LCD, Reset Host, or Power Off Host")
def power() -> None:
    pass


@power.command(help="Reboot the Crystalfontx LCD")
@async_command
@pass_timeout_retry
@pass_client
async def reboot_lcd(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.reboot_lcd(timeout, retry_times)


@power.command(help="Reset the host, assuming ATX control is configured")
@async_command
@pass_timeout_retry
@pass_client
async def reset_host(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.reset_host(timeout, retry_times)


@power.command(help="Turn the host's power off, assuming ATX control is configured")
@async_command
@pass_timeout_retry
@pass_client
async def shutdown_host(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.shutdown_host(timeout, retry_times)


@main.command(help="6 (0x06): Clear LCD Screen")
@async_command
@pass_timeout_retry
@pass_client
async def clear(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.clear_screen(timeout, retry_times)


@main.group(help="Set LCD contents for a line")
def line() -> None:
    pass


@line.command(name="1", help="7 (0x07): Set LCD Contents, Line 1")
@click.argument("line", type=BYTES)
@async_command
@pass_timeout_retry
@pass_client
async def set_line_1(
    client: DbusClient, line: bytes, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.set_line_1(line, timeout, retry_times)


@line.command(name="2", help="8 (0x08): Set LCD Contents, Line 2")
@click.argument("line", type=BYTES)
@async_command
@pass_timeout_retry
@pass_client
async def set_line_2(
    client: DbusClient, line: bytes, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.set_line_2(line, timeout, retry_times)


@main.command(help="Interact with special characters")
def character() -> None:
    raise NotImplementedError("character")


@main.group(help="Interact directly with the LCD controller")
def lcd() -> None:
    pass


@lcd.command(name="poke", help="10 (0x0A): Read 8 Bytes of LCD Memory")
@click.argument("address", type=BYTE)
@async_command
@pass_timeout_retry
@pass_client
async def read_lcd_memory(
    client: DbusClient, address: int, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    memory = await client.read_lcd_memory(address, timeout, retry_times)
    echo(LcdMemoryM.unpack(memory))


@main.group(help="Interact with the LCD cursor")
def cursor() -> None:
    pass


@cursor.command(name="position", help="11 (0x0B): Set LCD Cursor Position")
@click.argument("row", type=BYTE)
@click.argument("column", type=BYTE)
@async_command
@pass_timeout_retry
@pass_client
async def set_cursor_position(
    client: DbusClient,
    row: int,
    column: int,
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    await client.set_cursor_position(row, column, timeout, retry_times)


@cursor.command(name="style", help="12 (0x0C): Set LCD Cursor Style")
@click.argument("style", type=click.Choice([e.name for e in CursorStyle]))
@async_command
@pass_timeout_retry
@pass_client
async def set_cursor_style(
    client: DbusClient, style: str, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.set_cursor_style(
        CursorStyleM.pack(CursorStyle[style]), timeout, retry_times
    )


@main.command(help="13 (0x0D): Set LCD Contrast")
@click.argument("contrast", type=float)
@async_command
@pass_timeout_retry
@pass_client
async def contrast(
    client: DbusClient, contrast: float, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    await client.set_contrast(contrast, timeout, retry_times)


@main.command(help="14 (0x0E): Set LCD & Keypad Backlight")
@click.argument("brightness", type=float)
@click.option("--keypad", type=float)
@async_command
@pass_timeout_retry
@pass_client
async def backlight(
    client: DbusClient,
    brightness: float,
    keypad: Optional[float],
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    await client.set_backlight(
        brightness, KeypadBrightnessM.pack(keypad), timeout, retry_times
    )


@main.group(help="DOW (Dallas One-Wire) capabilities")
def dow() -> None:
    pass


@dow.command(name="info", help="18 (0x12): Read DOW Device Information")
@click.argument("index", type=BYTE)
@async_command
@pass_timeout_retry
@pass_client
async def read_dow_device_information(
    client: DbusClient, index: int, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    info = await client.read_dow_device_information(index, timeout, retry_times)
    echo(DowDeviceInformationM.unpack(info))


@main.group(help="Temperature reporting and live display")
def temperature() -> None:
    pass


@temperature.command(name="reporting", help="19 (0x13): Set Up Temperature Reporting")
@click.argument("enabled", nargs=-1)
@async_command
@pass_timeout_retry
@pass_client
async def setup_temperature_reporting(
    client: DbusClient,
    enabled: Tuple[int, ...],
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    await client.setup_temperature_reporting(list(enabled), timeout, retry_times)


@dow.command(name="transaction", help="20 (0x14): Arbitrary DOW Transaction")
@click.argument("index", type=BYTE)
@click.argument("bytes_to_read", type=BYTE)
@click.option("--data_to_write", type=BYTES)
@async_command
@pass_timeout_retry
@pass_client
async def dow_transaction(
    client: DbusClient,
    index: int,
    bytes_to_read: int,
    data_to_write: Optional[bytes],
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    res = await client.dow_transaction(
        index, bytes_to_read, OptBytesM.pack(data_to_write), timeout, retry_times
    )
    echo(DowTransactionResultM.unpack(res))


@temperature.command(name="display", help="21 (0x15): Set Up Live Temperature Display")
@click.argument("slot", type=BYTE)
@click.argument("index", type=BYTE)
@click.option("--n-digits", "-n", type=click.Choice(["3", "5"]), required=True)
@click.option("--column", "-c", type=BYTE, required=True)
@click.option("--row", "-r", type=BYTE, required=True)
@click.option("--units", "-U", type=click.Choice([e.name for e in TemperatureUnit]))
@async_command
@pass_timeout_retry
@pass_client
async def setup_live_temperature_display(
    client: DbusClient,
    slot: int,
    index: int,
    n_digits: str,
    column: int,
    row: int,
    units: str,
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    item = TemperatureDisplayItem(
        index=index,
        n_digits=cast(TemperatureDigits, int(n_digits)),
        column=column,
        row=row,
        units=TemperatureUnit[units],
    )

    await client.setup_live_temperature_display(
        slot, TemperatureDisplayItemM.pack(item), timeout, retry_times
    )


@lcd.command(name="send", help="22 (0x16): Send Command Directly to the LCD Controller")
@click.argument("location", type=click.Choice([e.name for e in LcdRegister]))
@click.argument("data", type=BYTE)
@async_command
@pass_timeout_retry
@pass_client
async def send_command_to_lcd_controler(
    client: DbusClient,
    location: str,
    data: int,
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    register = LcdRegister[location]
    await client.send_command_to_lcd_controller(
        LcdRegisterM.pack(register), data, timeout, retry_times
    )


@main.group(help="Interact with the keypad")
def keypad() -> None:
    pass


@keypad.command(name="reporting", help="23 (0x17): Configure Key Reporting")
@click.option(
    "--when-pressed", multiple=True, type=click.Choice(list(KEYPRESSES.keys()))
)
@click.option(
    "--when-released", multiple=True, type=click.Choice(list(KEYPRESSES.keys()))
)
@async_command
@pass_timeout_retry
@pass_client
async def configure_key_reporting(
    client: DbusClient,
    when_pressed: List[str],
    when_released: List[str],
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    await client.configure_key_reporting(
        [KEYPRESSES[name] for name in when_pressed],
        [KEYPRESSES[name] for name in when_released],
        timeout,
        retry_times,
    )


@keypad.command(name="poll", help="24 (0x18): Read Keypad, Polled Mode")
@async_command
@pass_timeout_retry
@pass_client
async def poll_keypad(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    polled = await client.poll_keypad(timeout, retry_times)
    echo(KeypadPolledM.unpack(polled))


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
@pass_timeout_retry
@pass_client
async def atx(
    client: DbusClient,
    function: List[str],
    auto_polarity: bool,
    power_pulse_length: float,
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    await client.set_atx_power_switch_functionality(
        (
            [AtxPowerSwitchFunction[fn].value for fn in function],
            auto_polarity,
            False,
            False,
            power_pulse_length,
        ),
        timeout,
        retry_times,
    )


@main.command(help="29 (0x1D): Enable/Disable and Reset the Watchdog")
@click.argument("timeout_seconds", type=WATCHDOG_SETTING)
@async_command
@pass_client
async def watchdog(
    client: DbusClient,
    timeout_seconds: int,
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    await client.configure_watchdog(timeout_seconds, timeout, retry_times)


@main.command(help="30 (0x1E): Read Reporting & Status")
@async_command
@pass_timeout_retry
@pass_client
async def status(
    client: DbusClient, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    status = await client.read_status(timeout, retry_times)
    echo(DeviceStatusM.unpack(status))


@main.command(help="31 (0x1F): Send Data to LCD")
@click.argument("row", type=int)
@click.argument("column", type=int)
@click.argument("data", type=BYTES)
@async_command
@pass_timeout_retry
@pass_client
async def send(
    client: DbusClient,
    row: int,
    column: int,
    data: bytes,
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    await client.send_data(row, column, data, timeout, retry_times)


@main.command(help="33 (0x21): Set Baud Rate")
@click.argument("rate", type=BAUD_RATE)
@click.option(
    "--save/--no-save",
    default=False,
    help="Save the new baud rate to the configuration",
)
@async_command
@pass_client
@pass_config
@click.pass_obj
async def baud(
    obj: Obj, staged: StagedConfig, client: DbusClient, rate: BaudRate, save: bool
) -> None:
    await client.set_baud_rate(rate, obj.timeout, obj.retry_times)

    if save:
        logger.info(f"Saving baud rate {rate} to {staged.target_config.file}")
        try:
            run_config_command(obj, staged, ["set", "baud_rate", str(rate)])
        except ValueError as exc:
            echo(str(exc))
            sys.exit(1)
        else:
            staged.reload_target()
        finally:
            if staged.dirty:
                warn_dirty()


@main.group(help="Interact with GPIO pins")
def gpio() -> None:
    pass


@gpio.command(name="set", help="34 (0x22): Set or Set and Configure GPIO Pins")
@click.argument("index", type=BYTE)
@click.argument("state", type=BYTE)
@click.option("--function", type=FUNCTION, help="The GPIO pin's function")
@click.option("--up", type=DRIVE_MODE, help="The GPIO pin's pull-up drive mode")
@click.option("--down", type=DRIVE_MODE, help="The GPIO pin's pull-down drive mode")
@async_command
@pass_timeout_retry
@pass_client
async def set_gpio(
    client: DbusClient,
    index: int,
    output_state: int,
    function: Optional[GpioFunction],
    up: Optional[GpioDriveMode],
    down: Optional[GpioDriveMode],
    timeout: TimeoutT,
    retry_times: RetryTimesT,
) -> None:
    settings = load_gpio_settings(function, up, down)
    await client.set_gpio(
        index, output_state, OptGpioSettingsM.pack(settings), timeout, retry_times
    )


@gpio.command(
    name="read", help="35 (0x23): Read GPIO Pin Levels and Configuration State"
)
@click.argument("index", type=BYTE)
@async_command
@pass_timeout_retry
@pass_client
async def read_gpio(
    client: DbusClient, index: int, timeout: TimeoutT, retry_times: RetryTimesT
) -> None:
    res = await client.read_gpio(index, timeout, retry_times)
    echo(GpioReadM.unpack(res))


@main.group(help="Run various effects, such as marquees")
@click.option("--tick", type=float, help="How often to update the effect")
@click.option("--for", "for_", type=float, help="Amount of time to run the effect for")
@click.pass_obj
def effects(obj: Obj, tick: Optional[float], for_: Optional[float]) -> None:
    obj.effect_options = EffectOptions(tick=tick, for_=for_)


def pass_effect_client(fn: AsyncCommand) -> AsyncCommand:
    @pass_client
    @functools.wraps(fn)
    async def wrapper(client: DbusClient, *args, **kwargs) -> None:
        effect_client = await DbusEffectClient.load(client)
        await fn(effect_client, *args, **kwargs)

    return wrapper


@effects.command(help="Display a marquee effect")
@click.argument("row", type=int)
@click.argument("text")
@click.option(
    "--pause", type=float, help="An amount of time to pause before starting the effect"
)
@async_command
@pass_effect_client
@click.pass_obj
async def marquee(
    obj: Obj, client: DbusEffectClient, row: int, text: str, pause: Optional[float]
) -> None:
    tick = obj.effect_options.tick if obj.effect_options else None
    for_ = obj.effect_options.for_ if obj.effect_options else None

    m = Marquee(client=client, row=row, text=text, pause=pause, tick=tick)

    await run_effect(m, asyncio.get_running_loop(), for_)


@effects.command(help="Display a screensaver-like effect")
@click.argument("text")
@async_command
@pass_effect_client
@click.pass_obj
async def screensaver(obj: Obj, client: DbusEffectClient, text: str) -> None:
    tick = obj.effect_options.tick if obj.effect_options else None
    for_ = obj.effect_options.for_ if obj.effect_options else None

    s = Screensaver(client=client, text=text, tick=tick)

    await run_effect(s, asyncio.get_running_loop(), for_)


@effects.command(help="Have a dance party!")
@async_command
@pass_effect_client
@click.pass_obj
async def dance_party(obj: Obj, client: DbusEffectClient) -> None:
    tick = obj.effect_options.tick if obj.effect_options else None
    for_ = obj.effect_options.for_ if obj.effect_options else None

    d = DanceParty(client=client, tick=tick)

    await run_effect(d, asyncio.get_running_loop(), for_)
