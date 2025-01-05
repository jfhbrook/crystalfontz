import asyncio
from dataclasses import dataclass
import functools
import logging
from typing import Callable, cast, Coroutine, Literal, Optional, Type

import click

from crystalfontz.baud import BaudRate, FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.client import Client, create_connection
from crystalfontz.config import Config, GLOBAL_FILE
from crystalfontz.report import NoopReportHandler, ReportHandler


@dataclass
class Obj:
    config: Config
    global_: bool
    port: str
    baud_rate: BaudRate


LogLevel = (
    Literal["DEBUG"]
    | Literal["INFO"]
    | Literal["WARNING"]
    | Literal["ERROR"]
    | Literal["CRITICAL"]
)


@click.group()
@click.option(
    "--global/--no-global",
    "global_",
    default=False,
    help="Load the global config file at {GLOBAL_FILE}",
)
@click.option(
    "--log-level",
    environ="CRYSTALFONTZ_LOG_LEVEL",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Set the log level",
)
@click.option(
    "--port",
    environ="CRYSTALFONTZ_PORT",
    help="The serial port the Crystalfontz LCD is connected to",
)
@click.option(
    "--baud",
    type=click.Choice([str(SLOW_BAUD_RATE), str(FAST_BAUD_RATE)]),
    environ="CRYSTALFONTZ_BAUD_RATE",
    help="The baud rate to use when connecting to the Crystalfontz LCD",
)
@click.pass_context
def main(
    ctx: click.Context,
    global_: bool,
    log_level: LogLevel,
    port: Optional[str],
    baud: Optional[str],
) -> None:
    baud_rate = cast(Optional[BaudRate], int(baud) if baud else None)
    config: Config = Config.from_file(file=GLOBAL_FILE if global_ else None)
    ctx.obj = Obj(
        config=config,
        global_=global_,
        port=port or config.port,
        baud_rate=baud_rate or config.baud_rate,
    )

    logging.basicConfig(level=getattr(logging, log_level))


AsyncCommand = Callable[..., Coroutine[None, None, None]]
WrappedAsyncCommand = Callable[..., None]
AsyncCommandDecorator = Callable[[AsyncCommand], WrappedAsyncCommand]


def client(
    run_forever: bool = False,
    report_handler_cls: Type[ReportHandler] = NoopReportHandler,
) -> AsyncCommandDecorator:
    def decorator(fn: AsyncCommand) -> WrappedAsyncCommand:
        @click.pass_context
        @functools.wraps(fn)
        def wrapped(ctx: click.Context, *args, **kwargs) -> None:
            port: str = ctx.obj.port
            baud_rate: BaudRate = ctx.obj.baud_rate

            async def main() -> None:
                client: Client = await create_connection(
                    port, report_handler=report_handler_cls(), baud_rate=baud_rate
                )
                await fn(client, *args, **kwargs)

            try:
                if run_forever:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.create_task(main())
                    loop.run_forever()
                else:
                    asyncio.run(main())
            except KeyboardInterrupt:
                pass

        return wrapped

    return decorator


@main.command()
def listen() -> None:
    """
    Listen for key and temperature reports. To configure which reports to
    receive, use 'crystalfontz keypad configure-reporting' and
    'crystalfontz temperature setup-reporting' respectively.
    """
    pass


@main.command(help="0 (0x00): Ping command")
@click.argument("payload")
@client()
async def ping(client: Client, payload: str) -> None:
    await client.ping(payload.encode("utf8"))


@main.command()
def versions() -> None:
    pass


@main.group()
def user_flash_area() -> None:
    pass


@user_flash_area.command(name="write")
def write_user_flash_area() -> None:
    pass


@user_flash_area.command(name="read")
def read_user_flash_area() -> None:
    pass


@main.command()
def store_boot_state() -> None:
    pass


@main.group()
def lcd() -> None:
    pass


@lcd.command(name="reboot")
def reboot_lcd() -> None:
    pass


@main.group()
def host() -> None:
    pass


@host.command(name="reset")
def reset_host() -> None:
    pass


@host.command(name="shutdown")
def shutdown_host() -> None:
    pass


@main.command()
def clear_screen() -> None:
    pass


@main.command()
def set_line_1() -> None:
    pass


@main.command()
def set_line_2() -> None:
    pass


@main.group()
def special_character() -> None:
    pass


@special_character.command(name="set-data")
def set_special_character_data() -> None:
    pass


@special_character.command(name="set-encoding")
def set_special_character_encoding() -> None:
    pass


@lcd.command(name="read_memory")
def read_lcd_memory() -> None:
    pass


@main.group()
def cursor() -> None:
    pass


@cursor.command(name="set-position")
def set_cursor_position() -> None:
    pass


@cursor.command(name="set-style")
def set_cursor_style() -> None:
    pass


@main.command()
def set_contrast() -> None:
    pass


@main.command()
def set_backlight() -> None:
    pass


@main.group()
def dow() -> None:
    pass


@dow.command(name="read-device-information")
def read_dow_device_information() -> None:
    pass


@main.group()
def temperature() -> None:
    pass


@temperature.command(name="setup-reporting")
def setup_temperature_reporting() -> None:
    pass


@dow.command(name="transaction")
def dow_transaction() -> None:
    pass


@temperature.command(name="setup-live-display")
def setup_live_temperature_display() -> None:
    pass


@lcd.command(name="send-command")
def send_command_to_lcd_controler() -> None:
    pass


@main.group()
def keypad() -> None:
    pass


@keypad.command(name="poll")
def poll_keypad() -> None:
    pass


@main.group()
def atx_power_switch() -> None:
    pass


@atx_power_switch.command(name="set-functionality")
def set_atx_power_switch_functionality() -> None:
    pass


@main.command()
def configure_watchdog() -> None:
    pass


@main.command()
def status() -> None:
    pass


@main.command()
def send() -> None:
    pass


@main.command()
def set_baud_rate() -> None:
    pass


@main.group()
def gpio() -> None:
    pass


@gpio.command(name="set")
def set_gpio() -> None:
    pass


@gpio.command(name="read")
def read_gpio() -> None:
    pass
