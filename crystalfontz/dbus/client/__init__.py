from typing import Any, cast, Optional, Self
from unittest.mock import Mock

from sdbus import SdBus  # pyright: ignore [reportMissingModuleSource]

from crystalfontz.config import Config
from crystalfontz.dbus.config import StagedConfig
from crystalfontz.dbus.domain import ConfigM
from crystalfontz.dbus.effects import DbusEffectClient
from crystalfontz.dbus.interface import DBUS_NAME, DbusInterface
from crystalfontz.dbus.report import DbusClientReportHandler


class DbusClient(DbusInterface):
    """
    A DBus client for the Crystalfontz device.
    """

    def __init__(
        self: Self,
        bus: Optional[SdBus] = None,
        report_handler: Optional[DbusClientReportHandler] = None,
    ) -> None:
        client = Mock(name="client", side_effect=NotImplementedError("client"))
        self.subscribe = Mock(name="client.subscribe")
        self._effect_client: Optional[DbusEffectClient] = None

        super().__init__(client, report_handler=report_handler)

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
