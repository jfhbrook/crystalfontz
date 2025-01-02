from abc import ABC, abstractmethod
import logging
from typing import Self

from crystalfontz.response import KeyActivityReport, TemperatureReport


class ReportHandler(ABC):
    @abstractmethod
    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        raise NotImplementedError("on_key_activity")

    @abstractmethod
    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        raise NotImplementedError("on_temperature")


class NoopReportHandler(ReportHandler):
    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        pass

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        pass


class LoggingReportHandler(ReportHandler):
    def __init__(self: Self) -> None:
        self.logger = logging.getLogger(__name__)

    async def on_key_activity(self: Self, report: KeyActivityReport) -> None:
        self.logger.info(report)

    async def on_temperature(self: Self, report: TemperatureReport) -> None:
        self.logger.info(report)
