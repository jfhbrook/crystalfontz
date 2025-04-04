from typing import Any, cast, Optional, Self
from unittest.mock import Mock

from sdbus import SdBus  # pyright: ignore [reportMissingModuleSource]

from crystalfontz.config import Config
from crystalfontz.dbus.config import StagedConfig
from crystalfontz.dbus.domain import ConfigM
from crystalfontz.dbus.interface import DBUS_NAME, DbusInterface


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

        active_config: Config = ConfigM.unpack(await self.config)

        return StagedConfig(
            target_config=Config.from_file(active_config.file),
            active_config=active_config,
        )
