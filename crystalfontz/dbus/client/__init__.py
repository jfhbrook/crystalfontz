from typing import Any, cast, Optional, Self
from unittest.mock import Mock

from sdbus import SdBus  # pyright: ignore [reportMissingModuleSource]

from crystalfontz.config import Config
from crystalfontz.dbus.config import StagedConfig
from crystalfontz.dbus.domain import ConfigM, RetryTimesM, TimeoutM
from crystalfontz.dbus.effects import DbusEffectClient
from crystalfontz.dbus.interface import DBUS_NAME, DbusInterface
from crystalfontz.dbus.report import DbusClientReportHandler
from crystalfontz.effects import Marquee, Screensaver


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

    async def effect_client(self: Self) -> DbusEffectClient:
        if not self._effect_client:
            self._effect_client = await DbusEffectClient.load(
                self, TimeoutM.none, RetryTimesM.none
            )
        return self._effect_client

    async def marquee(
        self: Self,
        row: int,
        text: str,
        pause: Optional[float] = None,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Marquee:
        """
        Display a marquee effect on the LCD screen.
        """

        client = await self.effect_client()

        return Marquee(
            row,
            text,
            client=client,
            pause=pause,
            tick=tick,
            timeout=timeout,
            retry_times=retry_times,
        )

    async def screensaver(
        self: Self,
        text: str,
        tick: Optional[float] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> Screensaver:
        """
        Display a screensaver effect on the LCD screen.
        """

        client = await self.effect_client()

        return Screensaver(
            text,
            client=client,
            tick=tick,
            timeout=timeout,
            retry_times=retry_times,
        )
