"""
`ReportHandler` derived classes for use with DBus interfaces.

This module is most likely to be used with the `DbusClient`. Of particular interest
will be the `DbusClientReportHandler`, and its subclasses
`DbusClientLoggingReportHandler` and `DbusClientCliReportHandler`.
"""

from abc import ABC
import asyncio
import json
import logging
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
    def __init__(self: Self) -> None:
        self.logger = logging.getLogger(__name__)
        self.iface: Optional[DbusInterfaceProtocol] = None

    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        if not self.iface:
            return

        try:
            self.iface.key_activity_reports.emit(KeyActivityReportM.pack(report))
        except Exception as exc:
            self.logger.error(exc)

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        if not self.iface:
            return

        try:
            self.iface.temperature_reports.emit(TemperatureReportM.pack(report))
        except Exception as exc:
            self.logger.error(exc)


class DbusClientReportHandler(DbusReportHandler):
    """
    A DBus report handler which listens to reports emitted by a dbus interface.

    This report handler is for use by DBus clients.
    """

    def __init__(self: Self) -> None:
        super().__init__()

        self._key_activity_task: Optional[asyncio.Task] = None
        self._temperature_task: Optional[asyncio.Task] = None

    async def listen(self: Self) -> None:
        """
        Listen for reports. Any reports emitted on the key_activity_reports and
        temperature_reports signals will be passed to the on_key_activity and
        on_temperature handler methods, respectively.
        """

        self._key_activity_task = asyncio.create_task(self._listen_key_activity())
        self._temperature_task = asyncio.create_task(self._listen_temperature())

    async def _listen_key_activity(self: Self) -> None:
        if self.iface:
            async for report in self.iface.key_activity_reports:
                await self.on_key_activity(KeyActivityReportM.unpack(report))

    async def _listen_temperature(self: Self) -> None:
        if self.iface:
            async for report in self.iface.temperature_reports:
                await self.on_temperature(TemperatureReportM.unpack(report))

    @property
    def done(self: Self) -> asyncio.Task[None]:
        """
        An asyncio.Task that resolves when the report handler is done listening. This
        is typically due to calling `report_handler.stop()`, but may be due to an
        exception.
        """

        return asyncio.create_task(self._done())

    async def _done(self: Self) -> None:
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

    def stop(self: Self) -> None:
        """
        Stop listening for reports.
        """

        if self._key_activity_task:
            self._key_activity_task.cancel()
        if self._temperature_task:
            self._temperature_task.cancel()


class DbusClientLoggingReportHandler(DbusClientReportHandler):
    """
    A DBus client report handler which logs, using Python's logging module.
    """

    def __init__(self: Self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        self.logger.info(report)

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        self.logger.info(report)


class DbusClientCliReportHandler(DbusClientReportHandler):
    """
    A DBus report handler intended for use by the client command line interface.
    """

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
