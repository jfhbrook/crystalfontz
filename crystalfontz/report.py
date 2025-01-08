from abc import ABC, abstractmethod
import json
import logging
from typing import Any

try:
    from typing import Self
except ImportError:
    Self = Any

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


class JsonReportHandler(ReportHandler):
    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        print(
            json.dumps(
                dict(type=report.__class__.__name__, activity=report.activity.name)
            )
        )

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        print(
            json.dumps(
                dict(
                    type=report.__class__.__name__,
                    celsius=report.celsius,
                    fahrenheit=report.fahrenheit,
                )
            )
        )
