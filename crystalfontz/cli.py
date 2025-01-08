import asyncio
from dataclasses import dataclass
import functools
import json
import logging
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
    Tuple,
    Type,
)
import warnings

try:
    from typing import Self
except ImportError:
    Self = Any

import click
from serial.serialutil import SerialException

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate, FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.client import Client, create_connection
from crystalfontz.config import Config, GLOBAL_FILE
from crystalfontz.cursor import CursorStyle
from crystalfontz.effects import Effect
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
from crystalfontz.report import JsonReportHandler, NoopReportHandler, ReportHandler
from crystalfontz.temperature import TemperatureDisplayItem, TemperatureUnit

logger = logging.getLogger(__name__)


@dataclass
class EffectOptions:
    tick: Optional[float]
    for_: Optional[float]


@dataclass
class Obj:
    config: Config
    global_: bool
    port: str
    model: str
    hardware_rev: Optional[str]
    firmware_rev: Optional[str]
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


class Byte(click.IntRange):
    name = "byte"

    def __init__(self: Self) -> None:
        super().__init__(min=0, max=255)


class WatchdogSetting(Byte):
    name = "watchdog_setting"

    def convert(
        self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]
    ) -> int:
        if value == "disable" or value == "disabled":
            return 0
        return super().convert(value, param, ctx)


BYTE = Byte()
WATCHDOG_SETTING = WatchdogSetting()


@click.group(help="Control your Crystalfontz device")
@click.option(
    "--global/--no-global",
    "global_",
    default=False,
    help=f"Load the global config file at {GLOBAL_FILE}",
)
@click.option("--config-file", "-C", type=click.Path(), help="A path to a config file")
@click.option(
    "--log-level",
    envvar="CRYSTALFONTZ_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="WARNING",
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
    timeout: Optional[float],
    retry_times: Optional[int],
    baud: Optional[str],
) -> None:
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
        timeout=timeout or config.timeout,
        retry_times=retry_times if retry_times is not None else config.retry_times,
        baud_rate=baud_rate or config.baud_rate,
    )

    logging.basicConfig(level=getattr(logging, log_level))


AsyncCommand = Callable[..., Coroutine[None, None, None]]
WrappedAsyncCommand = Callable[..., None]
AsyncCommandDecorator = Callable[[AsyncCommand], WrappedAsyncCommand]


def pass_client(
    run_forever: bool = False,
    report_handler_cls: Type[ReportHandler] = NoopReportHandler,
) -> AsyncCommandDecorator:
    def decorator(fn: AsyncCommand) -> WrappedAsyncCommand:
        @click.pass_context
        @functools.wraps(fn)
        def wrapped(ctx: click.Context, *args, **kwargs) -> None:
            port: str = ctx.obj.port
            model = ctx.obj.model
            hardware_rev = ctx.obj.hardware_rev
            firmware_rev = ctx.obj.firmware_rev
            timeout = ctx.obj.timeout
            retry_times = ctx.obj.retry_times
            baud_rate: BaudRate = ctx.obj.baud_rate

            async def main() -> None:
                try:
                    client: Client = await create_connection(
                        port,
                        model=model,
                        hardware_rev=hardware_rev,
                        firmware_rev=firmware_rev,
                        report_handler=report_handler_cls(),
                        timeout=timeout,
                        retry_times=retry_times,
                        baud_rate=baud_rate,
                    )
                except SerialException as exc:
                    click.echo(exc)
                    sys.exit(1)
                await fn(client, *args, **kwargs)
                if not run_forever:
                    client.close()
                await client.closed

            try:
                asyncio.run(main())
            except KeyboardInterrupt:
                pass

        return wrapped

    return decorator


@main.command(help="Listen for keypress and temperature reports")
@click.option("--for", "for_", type=float, help="Amount of time to run the effect for")
@pass_client(run_forever=True, report_handler_cls=JsonReportHandler)
async def listen(client: Client, for_: Optional[float]) -> None:
    """
    Listen for key and temperature reports. To configure which reports to
    receive, use 'crystalfontz keypad reporting' and
    'crystalfontz temperature reporting' respectively.
    """
    if for_ is not None:
        await asyncio.sleep(for_)
        client.close()


@main.command(help="0 (0x00): Ping command")
@click.argument("payload")
@pass_client()
async def ping(client: Client, payload: str) -> None:
    pong = await client.ping(payload.encode("utf8"))
    click.echo(pong.response)


@main.command(help="1 (0x01): Get Hardware & Firmware Version")
@pass_client()
async def versions(client: Client) -> None:
    versions = await client.versions()
    click.echo(f"{versions.model}: {versions.hardware_rev}, {versions.firmware_rev}")


@main.group(help="Interact with the User Flash Area")
def flash() -> None:
    pass


@flash.command(name="write", help="2 (0x02): Write User Flash Area")
@click.argument("data")
@pass_client()
async def write_user_flash_area(client: Client, data: str) -> None:
    # Click doesn't have a good way of receiving bytes as arguments.
    raise NotImplementedError("crystalfontz user-flash-area write")


@flash.command(name="read", help="3 (0x03): Read User Flash Area")
@pass_client()
async def read_user_flash_area(client: Client) -> None:
    flash = await client.read_user_flash_area()
    # TODO: Does this print as raw bytes?
    print(flash.data)


@main.command(help="4 (0x04): Store Current State as Boot State")
@pass_client()
async def store(client: Client) -> None:
    await client.store_boot_state()


@main.group(help="5 (0x05): Reboot LCD, Reset Host, or Power Off Host")
def power() -> None:
    pass


@power.command(help="Reboot the Crystalfontx LCD")
@pass_client()
async def reboot_lcd(client: Client) -> None:
    await client.reboot_lcd()


@power.command(help="Reset the host, assuming ATX control is configured")
@pass_client()
async def reset_host(client: Client) -> None:
    await client.reset_host()


@power.command(help="Turn the host's power off, assuming ATX control is configured")
@pass_client()
async def shutdown_host(client: Client) -> None:
    await client.shutdown_host()


@main.command(help="6 (0x06): Clear LCD Screen")
@pass_client()
async def clear(client: Client) -> None:
    await client.clear_screen()


@main.group(help="Set LCD contents for a line")
def line() -> None:
    pass


@line.command(name="1", help="7 (0x07): Set LCD Contents, Line 1")
@click.argument("line")
@pass_client()
async def set_line_1(client: Client, line: str) -> None:
    await client.set_line_1(line)


@line.command(name="2", help="8 (0x08): Set LCD Contents, Line 2")
@click.argument("line")
@pass_client()
async def set_line_2(client: Client, line: str) -> None:
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
    raise NotImplementedError("crystalfontz special-character")


@main.group(help="Interact directly with the LCD controller")
def lcd() -> None:
    pass


@lcd.command(name="poke", help="10 (0x0A): Read 8 Bytes of LCD Memory")
@click.argument("address", type=BYTE)
@pass_client()
async def read_lcd_memory(client: Client, address: int) -> None:
    memory = await client.read_lcd_memory(address)
    click.echo(bytes(memory.address) + b":" + memory.data)


@main.group(help="Interact with the LCD cursor")
def cursor() -> None:
    pass


@cursor.command(name="position", help="11 (0x0B): Set LCD Cursor Position")
@click.argument("row", type=BYTE)
@click.argument("column", type=BYTE)
@pass_client()
async def set_cursor_position(client: Client, row: int, column: int) -> None:
    await client.set_cursor_position(row, column)


@cursor.command(name="style", help="12 (0x0C): Set LCD Cursor Style")
@click.argument("style", type=click.Choice([e.name for e in CursorStyle]))
@pass_client()
async def set_cursor_style(client: Client, style: str) -> None:
    await client.set_cursor_style(CursorStyle[style])


@main.command(help="13 (0x0D): Set LCD Contrast")
@click.argument("contrast", type=float)
@pass_client()
async def contrast(client: Client, contrast: float) -> None:
    await client.set_contrast(contrast)


@main.command(help="14 (0x0E): Set LCD & Keypad Backlight")
@click.argument("brightness", type=float)
@click.option("--keypad", type=float)
@pass_client()
async def backlight(client: Client, brightness: float, keypad: Optional[float]) -> None:
    await client.set_backlight(brightness, keypad)


@main.group(help="DOW (Dallas One-Wire) capabilities")
def dow() -> None:
    pass


@dow.command(name="info", help="18 (0x12): Read DOW Device Information")
@click.argument("index", type=BYTE)
@pass_client()
async def read_dow_device_information(client: Client, index: int) -> None:
    info = await client.read_dow_device_information(index)
    click.echo(bytes(info.index) + b":" + info.rom_id)


@main.group(help="Temperature reporting and live display")
def temperature() -> None:
    pass


@temperature.command(name="reporting", help="19 (0x13): Set Up Temperature Reporting")
@click.argument("enabled", nargs=-1)
@pass_client()
async def setup_temperature_reporting(client: Client, enabled: Tuple[int]) -> None:
    await client.setup_temperature_reporting(enabled)


@dow.command(name="transaction", help="20 (0x14): Arbitrary DOW Transaction")
@click.argument("index", type=BYTE)
@click.argument("bytes_to_read", type=BYTE)
@click.option("--data_to_write")
def dow_transaction() -> None:
    #
    # This command also depends on being able to receive bytes from click.
    #
    raise NotImplementedError("crystalfontz dow transaction")


@temperature.command(name="display", help="21 (0x15): Set Up Live Temperature Display")
@click.argument("slot", type=BYTE)
@click.argument("index", type=BYTE)
@click.option("--n-digits", "-n", type=click.Choice(["3", "5"]), required=True)
@click.option("--column", "-c", type=BYTE, required=True)
@click.option("--row", "-r", type=BYTE, required=True)
@click.option("--units", "-U", type=click.Choice([e.name for e in TemperatureUnit]))
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
@pass_client()
async def send_command_to_lcd_controler(
    client: Client, location: str, data: int
) -> None:
    await client.send_command_to_lcd_controller(LcdRegister[location], data)


@main.group(help="Interact with the keypad")
def keypad() -> None:
    pass


KEYPRESSES: Dict[str, KeyPress] = dict(
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
@pass_client()
async def configure_key_reporting(
    client: Client, when_pressed: List[str], when_released: List[str]
) -> None:
    await client.configure_key_reporting(
        when_pressed={KEYPRESSES[name] for name in when_pressed},
        when_released={KEYPRESSES[name] for name in when_released},
    )


@keypad.command(name="poll", help="24 (0x18): Read Keypad, Polled Mode")
@pass_client()
async def poll_keypad(client: Client) -> None:
    polled = await client.poll_keypad()
    click.echo(json.dumps(polled.states.as_dict(), indent=2))


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
@pass_client()
async def watchdog(client: Client, timeout_seconds: int) -> None:
    await client.configure_watchdog(timeout_seconds)


@main.command(help="30 (0x1E): Read Reporting & Status")
@pass_client()
async def status(client: Client) -> None:
    status = await client.read_status()

    if hasattr(status, "temperature_sensors_enabled"):
        enabled = ", ".join(sorted(list(status.temperature_sensors_enabled)))
        click.echo(f"Temperature sensors enabled: {enabled}")

    if hasattr(status, "key_states"):
        click.echo("Key states:")
        click.echo(json.dumps(status.key_states.as_dict(), indent=2))

    if hasattr(status, "atx_power_switch_functionality_settings"):
        settings = status.atx_power_switch_functionality_settings
        click.echo("ATX Power Switch Functionality Settings:")
        click.echo(
            f"  Functions enabled: {', '.join([e.name for e in settings.functions])}"
        )
        click.echo(f"  Auto-polarity Enabled: {settings.auto_polarity}")
        click.echo(
            f"  Power Pulse Length (Seconds): {settings.power_pulse_length_seconds}"
        )

    if hasattr(status, "watchdog_counter"):
        click.echo(f"Watchdog counter: {status.watchdog_counter}")

    if hasattr(status, "contrast"):
        click.echo(f"Contrast: {status.contrast}")

    if hasattr(status, "cfa633_contrast"):
        click.echo(f"Contrast (CFA633 compatible): {status.cfa633_contrast}")

    if hasattr(status, "keypad_brightness") or hasattr(status, "lcd_brightness"):
        click.echo("Backlight:")
        if hasattr(status, "keypad_brightness"):
            click.echo(f"  Keypad Backlight Brightness: {status.keypad_brightness}")
        if hasattr(status, "lcd_brightness"):
            click.echo(f"  LCD Backlight Brightness: {status.lcd_brightness}")


@main.command(help="31 (0x1F): Send Data to LCD")
@click.argument("row", type=int)
@click.argument("column", type=int)
@click.argument("data")
@pass_client()
async def send(client: Client, row: int, column: int, data: str) -> None:
    await client.send_data(row, column, data)


@main.command(help="33 (0x21): Set Baud Rate")
def baud() -> None:
    #
    # Setting the baud rate will more or less require updating the config
    # file. The correct behavior needs to be sussed out.
    #
    raise NotImplementedError("crystalfontz baud")


@main.group(help="Interact with GPIO pins")
def gpio() -> None:
    pass


@gpio.command(name="set", help="34 (0x22): Set or Set and Configure GPIO Pins")
def set_gpio() -> None:
    raise NotImplementedError("crystalfontz gpio set")


@gpio.command(
    name="read", help="35 (0x23): Read GPIO Pin Levels and Configuration State"
)
def read_gpio() -> None:
    raise NotImplementedError("crystalfontz gpio read")


@main.group(help="Run various effects, such as marquees")
@click.option("--tick", type=float, help="How often to update the effect")
@click.option("--for", "for_", type=float, help="Amount of time to run the effect for")
@click.pass_context
def effects(ctx: click.Context, tick: Optional[float], for_: Optional[float]) -> None:
    ctx.obj.effect_options = EffectOptions(tick=tick, for_=for_)


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
@pass_client()
@click.pass_context
async def marquee(
    ctx: click.Context, client: Client, row: int, text: str, pause: Optional[float]
) -> None:
    tick = ctx.obj.effect_options.tick
    for_ = ctx.obj.effect_options.for_
    m = client.marquee(row, text, pause=pause, tick=tick)

    await run_effect(m, client.loop, for_)


@effects.command(help="Display a screensaver-like effect")
@click.argument("text")
@pass_client()
@click.pass_context
async def screensaver(ctx: click.Context, client: Client, text: str) -> None:
    tick = ctx.obj.effect_options.tick
    for_ = ctx.obj.effect_options.for_
    s = client.screensaver(text, tick=tick)

    await run_effect(s, client.loop, for_)
