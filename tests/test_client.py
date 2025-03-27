import asyncio
import logging
from typing import Self
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from serial_asyncio import SerialTransport

from crystalfontz.client import Client
from crystalfontz.device import CFA533, Device
from crystalfontz.error import DeviceError, ResponseDecodeError, UnknownResponseError
from crystalfontz.packet import Packet
from crystalfontz.report import ReportHandler
from crystalfontz.response import code, KeyActivityReport, Pong, Response

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


@pytest_asyncio.fixture
async def client(
    device: Device, report_handler: ReportHandler, transport: SerialTransport
) -> Client:
    client = Client(
        device=device,
        report_handler=report_handler,
        timeout=0.1,
        retry_times=0,
        loop=asyncio.get_running_loop(),
    )
    client._is_serial_transport = Mock(return_value=True)
    client.connection_made(transport)
    return client


@code(0x64)
class BrokenResponse(Response):
    def __init__(self: Self, data: bytes) -> None:
        raise Exception("oops!")


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
    rcv = client.subscribe(Pong)
    client._packet_received((0x40, b"ping!"))

    # Timeout is in case errors aren't properly raised by the receiver
    async with asyncio.timeout(0.2):
        exc, res = await rcv.get()

    client.unsubscribe(Pong, rcv)

    assert exc is None
    assert isinstance(res, Pong)
    assert res.response == b"ping!"

    client.close()

    await client.closed


@pytest.mark.asyncio
async def test_device_error(client: Client) -> None:
    rcv = client.subscribe(Pong)
    client._packet_received((0b11000000, b"ping!"))

    async with asyncio.timeout(0.2):
        exc, res = await rcv.get()

    client.unsubscribe(Pong, rcv)

    assert isinstance(exc, DeviceError)
    assert exc.command == 0x00
    assert exc.expected_response == 0x40
    assert res is None

    client.close()

    await client.closed


@pytest.mark.asyncio
async def test_device_error_no_sub(client: Client) -> None:
    client._packet_received((0b11000000, b"ping!"))

    await asyncio.sleep(0.1)

    with pytest.raises(DeviceError):
        await client.closed


@pytest.mark.asyncio
async def test_arbitrary_error(client: Client, monkeypatch) -> None:
    monkeypatch.setattr(
        "crystalfontz.response.Response.from_packet",
        Mock(name="Response.from_packet()", side_effect=Exception("oops!")),
    )

    rcv = client.subscribe(Pong)

    # Need to manually mark as receiving, since we don't actually call
    # rcv.get() until after we call _packet_received. Recall that nothing in
    # a coroutine gets called until it is awaited. In practice, the user
    # would have called rcv.get() async.
    rcv._set_receiving()

    client._packet_received((0x40, b"ping!"))

    async with asyncio.timeout(1.0):
        exc, res = await rcv.get()

    client.unsubscribe(Pong, rcv)

    assert isinstance(exc, Exception)
    assert res is None

    client.close()

    await client.closed


@pytest.mark.asyncio
async def test_arbitrary_error_no_sub(client: Client, monkeypatch) -> None:
    monkeypatch.setattr(
        "crystalfontz.response.Response.from_packet",
        Mock(name="Response.from_packet()", side_effect=Exception("oops!")),
    )

    client._packet_received((0x40, b"ping!"))

    await asyncio.sleep(0.1)

    with pytest.raises(Exception):
        await client.closed


@pytest.mark.asyncio
async def test_response_decode_error(client: Client) -> None:
    q = client.subscribe(BrokenResponse)
    client._packet_received((0x64, b"oops!"))

    async with asyncio.timeout(0.2):
        exc, res = await q.get()

    client.unsubscribe(BrokenResponse, q)

    assert isinstance(exc, ResponseDecodeError)
    assert exc.response_cls is BrokenResponse
    assert res is None

    client.close()

    await client.closed


@pytest.mark.asyncio
async def test_response_decode_error_no_sub(client: Client) -> None:
    client._packet_received((0x64, b"oops!"))

    await asyncio.sleep(0.1)

    with pytest.raises(ResponseDecodeError):
        await client.closed


@pytest.mark.asyncio
async def test_unknown_response(client: Client) -> None:
    client._packet_received((0x00, b"wat"))

    with pytest.raises(UnknownResponseError):
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
