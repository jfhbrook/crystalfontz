import functools
import logging
from typing import Optional

import click
from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    sd_bus_open_system,
    sd_bus_open_user,
    set_default_bus,
)

from crystalfontz.cli import SyncCommand

logger = logging.getLogger(__name__)

BusType = Optional[bool]
BUS_TYPE = click.BOOL

DEFAULT_BUS = None
USER_BUS = True
SYSTEM_BUS = False


def bus_type_option(fn: SyncCommand) -> SyncCommand:
    @click.option(
        "--user/--system",
        type=BUS_TYPE,
        default=DEFAULT_BUS,
        help="Connect to either the user or system bus",
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs) -> None:
        user = kwargs.pop("user")
        kwargs["bus_type"] = user
        return fn(*args, **kwargs)

    return wrapper


def configure_bus(bus_type: BusType) -> None:
    if bus_type is USER_BUS:
        logger.info("Connecting to the user session bus")
        set_default_bus(sd_bus_open_user())
    elif bus_type is SYSTEM_BUS:
        logger.info("Connecting to the system bus")
        set_default_bus(sd_bus_open_system())
    else:
        logger.info("Connecting to the default bus")
