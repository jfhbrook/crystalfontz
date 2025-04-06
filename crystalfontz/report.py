from abc import ABC, abstractmethod
import json
import logging
from typing import Optional, Self

from crystalfontz.format import OutputMode
from crystalfontz.response import KeyActivityReport, TemperatureReport


class ReportHandler(ABC):
    """
    Handle reporting. Reports are issued for key activities and temperature readings.
    """

    @abstractmethod
    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        """
        This method is called on any new key activity report.
        """

        raise NotImplementedError("on_key_activity")

    @abstractmethod
    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        """
        This method is called on any new temperature report.
        """

        raise NotImplementedError("on_temperature")


class NoopReportHandler(ReportHandler):
    """
    A report handler which does nothing.
    """

    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        pass

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        pass


class LoggingReportHandler(ReportHandler):
    """
    A report handler which logs, using Python's logging module.
    """

    def __init__(self: Self) -> None:
        self.logger = logging.getLogger(__name__)

    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        self.logger.info(report)

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        self.logger.info(report)


class CliReportHandler(ReportHandler):
    """
    A report handler intended for use by the command line interface.
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
