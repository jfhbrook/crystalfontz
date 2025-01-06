import asyncio
import logging
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from serial_asyncio import SerialTransport

from crystalfontz.client import Client
from crystalfontz.command import Ping
from crystalfontz.device import CFA533, Device
from crystalfontz.error import DeviceError, ResponseDecodeError
from crystalfontz.packet import Packet
from crystalfontz.report import ReportHandler
from crystalfontz.response import KeyActivityReport, Pong

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


@pytest.mark.asyncio
async def test_close_success(client: Client) -> None:
    client._close()

    await client.closed


@pytest.mark.asyncio
async def test_close_exc(client: Client) -> None:
    client._close(Exception("ponyyy"))

    with pytest.raises(Exception):
        await client.closed


@pytest.mark.asyncio
async def test_ping_success(client: Client) -> None:
    q = client.subscribe(Pong)
    client._packet_received((0x00, b"ping!"))
    async with asyncio.timeout(0.2):
        exc, res = await q.get()
    client.unsubscribe(Pong, q)

    assert exc is None
    assert isinstance(res, Pong)
    assert res.response == b"ping!"

    client.close()

    await client.closed


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

    client.close()

    await client.closed

    getattr(report_handler, method).assert_called()


@pytest.mark.parametrize(
    "exc",
    [
        DeviceError(packet=(0b11000000 ^ 0x80, b"")),
        ResponseDecodeError(response_cls=KeyActivityReport, message="oops!"),
    ],
)
@pytest.mark.asyncio
async def test_report_handler_exception(
    client: Client, report_handler: ReportHandler, exc: Exception
) -> None:
    client._emit(KeyActivityReport, (exc, None))

    with pytest.raises(exc.__class__):
        await client.closed
