import asyncio
import logging
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from serial_asyncio import SerialTransport

from crystalfontz.client import Client
from crystalfontz.device import CFA533, Device
from crystalfontz.packet import Packet
from crystalfontz.report import ReportHandler

logging.basicConfig(level="DEBUG")


@pytest.fixture
def device() -> Device:
    return CFA533()


@pytest.fixture
def report_handler() -> ReportHandler:
    handler = Mock(name="MockReportHandler()")

    handler.on_key_activity = AsyncMock(name="MockReportHandler().on_key_activity")
    handler.on_temperature = AsyncMock(name="MockReportHandler().on_temperature")

    return handler


@pytest.fixture
def transport() -> SerialTransport:
    return Mock(name="SerialTransport()")


@pytest_asyncio.fixture(scope="function")
async def client(
    device: Device, report_handler: ReportHandler, transport: SerialTransport
) -> Client:
    client = Client(
        device=device, report_handler=report_handler, loop=asyncio.get_running_loop()
    )
    client._is_serial_transport = Mock(return_value=True)
    client.connection_made(transport)
    return client


@pytest.mark.parametrize(
    "packet,method",
    [
        ((0x80, b"\x01"), "on_key_activity"),
        ((0x82, b"\x01\x01\x00\xff"), "on_temperature"),
    ],
)
@pytest.mark.asyncio
async def test_report_handler(
    client: Client, report_handler: ReportHandler, packet: Packet, method: str
) -> None:
    client._packet_received(packet)

    await asyncio.sleep(0.1)

    await client.close()

    getattr(report_handler, method).assert_called()
