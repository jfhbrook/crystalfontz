import asyncio
import logging
from typing import Optional, Self

from sdbus import (  # pyright: ignore [reportMissingModuleSource];
    # dbus_method_async,
    dbus_property_async,
    # dbus_signal_async,
    DbusInterfaceCommonAsync,
    # DbusUnprivilegedFlag,
)

from crystalfontz.client import Client, create_connection
from crystalfontz.config import Config
from crystalfontz.dbus.config import ConfigStruct

logger = logging.getLogger(__name__)

DBUS_NAME = "org.jfhbrook.crystalfontz"


async def load_client(config_file: Optional[str]) -> Client:
    config: Config = Config.from_file(config_file)

    client = await create_connection(config.port)

    return client


class DbusInterface(  # type: ignore
    DbusInterfaceCommonAsync, interface_name=DBUS_NAME  # type: ignore
):
    """
    A DBus interface for controlling the Crystalfontz device.
    """

    def __init__(self: Self, client: Client, config_file: Optional[str] = None) -> None:
        super().__init__()
        self._config: Config = Config.from_file(config_file)
        self.client: Client = client
        self._client_lock: asyncio.Lock = asyncio.Lock()

    @dbus_property_async("(sssssqdq)")
    def config(self: Self) -> ConfigStruct:
        """
        The DBus service's currently loaded configuration.
        """

        config = self._config

        return (
            config.file or "",
            config.port,
            config.model,
            config.hardware_rev or "",
            config.firmware_rev or "",
            config.baud_rate,
            config.timeout,
            config.retry_times,
        )

    async def close(self: Self) -> None:
        """
        Unsubscribe from events and close the client.
        """

        async with self._client_lock:
            self.client.close()
            await self.client.closed

    @property
    def closed(self: Self) -> asyncio.Future:
        """
        A Future that resolves when the client is closed.
        """

        return self.client.closed
