from abc import ABC
import asyncio
import json
from typing import Any, Optional, Protocol, Self, TypeVar

from crystalfontz.dbus.domain import (
    KeyActivityReportM,
    TemperatureReportM,
)
from crystalfontz.format import OutputMode
from crystalfontz.report import (
    KeyActivityReport,
    ReportHandler,
    TemperatureReport,
)

T = TypeVar("T")


class DbusInterfaceProtocol(Protocol):
    # These types are NOT DbusSignalAsync[T]. They're defined as such in the
    # interface class, but are modified by metaclass. This gets pretty
    # confusing for the type checker! So in this case, we cheese it.
    key_activity_reports: Any
    temperature_reports: Any


class DbusReportHandler(ReportHandler, ABC):
    def __init__(self: Self) -> None:
        self.iface: Optional[DbusInterfaceProtocol] = None


class DbusInterfaceReportHandler(DbusReportHandler):
    """
    A report handler which emits reports on a supplied interface.
    """

    def __init__(self: Self) -> None:
        self.iface: Optional[DbusInterfaceProtocol] = None

    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        if not self.iface:
            return

        self.iface.key_activity_reports.emit(KeyActivityReportM.pack(report))

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        if not self.iface:
            return

        self.iface.temperature_reports.emit(TemperatureReportM.pack(report))


class DbusClientReportHandler(DbusReportHandler):
    """
    A report handler which listens to reports emitted by a dbus interface.
    """

    def __init__(self: Self) -> None:
        super().__init__()

        self._key_activity_task: Optional[asyncio.Task] = None
        self._temperature_task: Optional[asyncio.Task] = None

    async def _listen_key_activity(self: Self) -> None:
        if self.iface:
            async for report in self.iface.key_activity_reports:
                await self.on_key_activity(KeyActivityReportM.unpack(report))

    async def _listen_temperature(self: Self) -> None:
        if self.iface:
            async for report in self.iface.temperature_reports:
                await self.on_temperature(TemperatureReportM.unpack(report))

    async def listen(self: Self) -> None:
        self._key_activity_task = asyncio.create_task(self._listen_key_activity())
        self._temperature_task = asyncio.create_task(self._listen_temperature())

    async def _wait(self: Self) -> None:
        if self._key_activity_task:
            try:
                await self._key_activity_task
            except asyncio.CancelledError:
                pass

        if self._temperature_task:
            try:
                await self._temperature_task
            except asyncio.CancelledError:
                pass

    async def stop(self: Self) -> None:
        if self._key_activity_task:
            self._key_activity_task.cancel()
        if self._temperature_task:
            self._temperature_task.cancel()

        await self._wait()


class DbusClientCliReportHandler(DbusClientReportHandler):
    mode: Optional[OutputMode] = None

    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        if self.mode == "json":
            print(json.dumps(report.as_dict()))
        elif self.mode == "text":
            print(repr(report))

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        if self.mode == "json":
            print(json.dumps(report.as_dict()))
        elif self.mode == "text":
            print(repr(report))
