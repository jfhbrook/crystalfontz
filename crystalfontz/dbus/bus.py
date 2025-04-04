import logging
from typing import Optional

from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    sd_bus_open_system,
    sd_bus_open_user,
    set_default_bus,
)

logger = logging.getLogger(__name__)

BusType = Optional[bool]

DEFAULT_BUS = None
USER_BUS = True
SYSTEM_BUS = False


def configure_bus(bus_type: BusType) -> None:
    if bus_type is USER_BUS:
        logger.info("Connecting to the user session bus")
        set_default_bus(sd_bus_open_user())
    elif bus_type is SYSTEM_BUS:
        logger.info("Connecting to the system bus")
        set_default_bus(sd_bus_open_system())
    else:
        logger.info("Connecting to the default bus")
