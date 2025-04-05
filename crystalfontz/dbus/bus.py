import logging

from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    sd_bus_open_system,
    sd_bus_open_user,
    set_default_bus,
)

logger = logging.getLogger(__name__)


def select_session_bus() -> None:
    logger.debug("Connecting to the user session bus")
    set_default_bus(sd_bus_open_user())


def select_system_bus() -> None:
    logger.debug("Connecting to the system bus")
    set_default_bus(sd_bus_open_system())
