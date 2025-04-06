"""
Functions for creating and serving a DBus service.

Typically, the DBus service will be executed through the CLI interface, for
instance with:

```bash
python3 -m crystalfontz.dbus.service
```

However, these functions may be useful if you want to embed the DBus service within
another program.
"""

import logging
from typing import Optional

from sdbus import (  # pyright: ignore [reportMissingModuleSource]
    request_default_bus_name_async,
)

from crystalfontz.dbus.error import handle_dbus_error
from crystalfontz.dbus.interface import (
    DBUS_NAME,
    DbusInterface,
    load_client,
)
from crystalfontz.dbus.report import DbusInterfaceReportHandler

logger = logging.getLogger(__name__)


async def service(config_file: Optional[str] = None) -> DbusInterface:
    """
    Create a configure DBus service with a supplied config file.
    """

    report_handler = DbusInterfaceReportHandler()
    client = await load_client(report_handler=report_handler, config_file=config_file)
    iface = DbusInterface(
        client, report_handler=report_handler, config_file=config_file
    )

    logger.debug(f"Requesting bus name {DBUS_NAME}...")
    await request_default_bus_name_async(DBUS_NAME)

    logger.debug("Exporting interface to path /...")

    iface.export_to_dbus("/")

    logger.info(f"Listening on {DBUS_NAME} /")

    return iface


async def serve(config_file: Optional[str] = None) -> None:
    """
    Create and serve configure DBus service with a supplied config file.
    """

    async with handle_dbus_error(logger):
        srv = await service(config_file)

        await srv.closed


__all__ = ["service", "serve"]
