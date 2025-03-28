import asyncio
import logging
from typing import Optional, Self, Tuple

from sdbus import (  # pyright: ignore [reportMissingModuleSource];; dbus_signal_async,
    dbus_method_async,
    dbus_property_async,
    DbusInterfaceCommonAsync,
    DbusUnprivilegedFlag,
)

from crystalfontz.client import Client, create_connection
from crystalfontz.config import Config
from crystalfontz.dbus.config import ConfigStruct
from crystalfontz.dbus.map import (
    baud_rate_t,
    load_retry_times,
    load_timeout,
    retry_times_t,
    timeout_t,
)
from crystalfontz.error import ConnectionError

Ok = bool

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

    @dbus_property_async(f"(sssss{baud_rate_t}{timeout_t}{retry_times_t})")
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

    @dbus_method_async(f"y{timeout_t}{retry_times_t}", "y", flags=DbusUnprivilegedFlag)
    async def ping(
        self: Self,
        payload: bytes,
        timeout: float,
        retry_times: int,
    ) -> bytes:
        pong = await self.client.ping(
            payload, load_timeout(timeout), load_retry_times(retry_times)
        )
        return pong.response

    @dbus_method_async(f"{timeout_t}{retry_times_t}", "b", flags=DbusUnprivilegedFlag)
    async def test_connection(self: Self, timeout: float, retry_times: int) -> Ok:
        try:
            await self.client.test_connection(
                load_timeout(timeout), load_retry_times(retry_times)
            )
        except ConnectionError:
            return False
        else:
            return True

    # TODO: Should receive timeout and retry_times
    @dbus_method_async("", baud_rate_t, flags=DbusUnprivilegedFlag)
    async def detect_baud_rate(self: Self) -> int:
        # Detect the baud rate, as you do
        await self.client.detect_baud_rate()

        # Save to the loaded config
        self._config.baud_rate = self.client.baud_rate

        # Return the new baud rate
        return self.client.baud_rate

    @dbus_method_async(
        f"{timeout_t}{retry_times_t}", "(sss)", flags=DbusUnprivilegedFlag
    )
    async def versions(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> Tuple[str, str, str]:
        versions = await self.client.versions(
            load_timeout(timeout), load_retry_times(retry_times)
        )
        return (versions.model, versions.hardware_rev, versions.firmware_rev)

    @dbus_method_async(
        f"{timeout_t}{retry_times_t}", "(sss)", flags=DbusUnprivilegedFlag
    )
    async def detect_device(
        self: Self, timeout: float, retry_times: int
    ) -> Tuple[str, str, str]:
        await self.client.detect_device(
            load_timeout(timeout), load_retry_times(retry_times)
        )
        return (
            self.client.device.model,
            self.client.device.hardware_rev,
            self.client.device.firmware_rev,
        )
