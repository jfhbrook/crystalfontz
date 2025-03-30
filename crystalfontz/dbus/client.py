import asyncio
from dataclasses import dataclass
import functools
import logging
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from typing import Any, cast, List, Optional, Self
from unittest.mock import Mock

import click
from sdbus import sd_bus_open_system, sd_bus_open_user, SdBus

from crystalfontz.cli import (
    async_command,
    AsyncCommand,
    BYTES,
    echo,
    LogLevel,
    OutputMode,
)
from crystalfontz.config import Config
from crystalfontz.dbus.config import StagedConfig
from crystalfontz.dbus.error import handle_dbus_error
from crystalfontz.dbus.interface import DBUS_NAME, DbusInterface
from crystalfontz.dbus.map import RetryTimesM, TimeoutM, VersionsM

logger = logging.getLogger(__name__)


class DbusClient(DbusInterface):
    """
    A DBus client for the Crystalfontz device.
    """

    def __init__(self: Self, bus: Optional[SdBus] = None) -> None:
        client = Mock(name="client", side_effect=NotImplementedError("client"))
        self.subscribe = Mock(name="client.subscribe")
        super().__init__(client)

        cast(Any, self)._proxify(DBUS_NAME, "/", bus=bus)

    async def staged_config(self: Self) -> StagedConfig:
        """
        Fetch the state of staged configuration changes.
        """

        (
            file,
            port,
            model,
            hardware_rev,
            firmware_rev,
            baud_rate,
            timeout,
            retry_times,
        ) = await self.config

        active_config: Config = cast(Any, Config)(
            file=file,
            port=port,
            model=model,
            hardware_rev=hardware_rev if hardware_rev else None,
            firmware_rev=firmware_rev if firmware_rev else None,
            baud_rate=baud_rate,
            timeout=timeout,
            retry_times=retry_times,
        )

        return StagedConfig(
            target_config=Config.from_file(file),
            active_config=active_config,
        )


@dataclass
class Obj:
    client: DbusClient
    log_level: LogLevel
    output: OutputMode
    user: bool


def pass_config(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        config = await obj.client.staged_config()
        await fn(config, *args, **kwargs)

    return wrapped


def pass_client(fn: AsyncCommand) -> AsyncCommand:
    @click.pass_obj
    @functools.wraps(fn)
    async def wrapped(obj: Obj, *args, **kwargs) -> None:
        async with handle_dbus_error(logger):
            await fn(obj.client, *args, **kwargs)

    return wrapped


def should_sudo(config_file: str) -> bool:
    st = os.stat(config_file)
    return os.geteuid() != st.st_uid


def run_config_command(obj: Obj, staged: StagedConfig, argv: List[str]) -> None:
    plusdeck_bin = str(Path(__file__).parent.parent / "cli.py")
    args: List[str] = [
        sys.executable,
        plusdeck_bin,
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

    sudo system ctl restart plusdeck"""
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
    "--user/--no-user", type=bool, default=False, help="Connect to the user bus"
)
@click.pass_context
def main(
    ctx: click.Context, log_level: LogLevel, output: OutputMode, user: bool
) -> None:
    """
    Control your Crystalfontz device.
    """

    logging.basicConfig(level=getattr(logging, log_level))

    # Set the output mode for echo
    echo.mode = output

    async def load() -> None:
        bus: SdBus = sd_bus_open_user() if user else sd_bus_open_system()
        client = DbusClient(bus)
        ctx.obj = Obj(client=client, log_level=log_level, output=output, user=user)

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
        baud_rate = await client.detect_baud_rate()

    if device:
        model, hardware_rev, firmware_rev = await client.detect_device(
            TimeoutM.none, RetryTimesM.none
        )

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


@main.command(help="0 (0x00): Ping command")
@click.argument("payload", type=BYTES)
@async_command
@pass_client
async def ping(client: DbusClient, payload: bytes) -> None:
    pong = await client.ping(payload, TimeoutM.none, RetryTimesM.none)
    echo(pong)


@main.command(help="1 (0x01): Get Hardware & Firmware Version")
@async_command
@pass_client
async def versions(client: DbusClient) -> None:
    versions = await client.versions(TimeoutM.none, RetryTimesM.none)
    echo(VersionsM.load(versions))


@main.group(help="Interact with the User Flash Area")
def flash() -> None:
    pass


@flash.command(name="write", help="2 (0x02): Write User Flash Area")
@click.argument("data", type=BYTES)
@async_command
@pass_client
async def write_user_flash_area(client: DbusClient, data: bytes) -> None:
    await client.write_user_flash_area(data, TimeoutM.none, RetryTimesM.none)


@flash.command(name="read", help="3 (0x03): Read User Flash Area")
@async_command
@pass_client
async def read_user_flash_area(client: DbusClient) -> None:
    flash = await client.read_user_flash_area(TimeoutM.none, RetryTimesM.none)
    echo(flash)


if __name__ == "__main__":
    main()
