import asyncio
from collections import defaultdict
from typing import cast, Dict, List, Optional, Self, Type, TypeVar

from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

from crystalfontz.command import (
    Command,
    GetVersions,
    Ping,
    ReadStatus,
    SetLine1,
    SetLine2,
)
from crystalfontz.device import Device, DEVICES, DeviceStatus
from crystalfontz.error import ConnectionError
from crystalfontz.packet import Packet, parse_packet, serialize_packet
from crystalfontz.report import NoopReportHandler, ReportHandler
from crystalfontz.response import (
    KeyActivityReport,
    Pong,
    Response,
    SetLine1Response,
    SetLine2Response,
    StatusResponse,
    TemperatureReport,
    Versions,
)

R = TypeVar("R", bound=Response)


class Client(asyncio.Protocol):
    def __init__(
        self: Self,
        device: Device,
        report_handler: ReportHandler,
        loop: asyncio.AbstractEventLoop,
    ) -> None:

        self.device: Device = device
        self._report_handler: ReportHandler = report_handler

        self._buffer: bytes = b""
        self._loop: asyncio.AbstractEventLoop = loop
        self._transport: Optional[SerialTransport] = None
        self._connection_made: asyncio.Future[None] = self._loop.create_future()

        self._expect: Optional[Type[Response]] = None
        self._queues: Dict[Type[Response], List[asyncio.Queue[Response]]] = defaultdict(
            lambda: list()
        )

    def connection_made(self: Self, transport) -> None:
        if not isinstance(transport, SerialTransport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport
        self._running = True

        self._key_activity_queue: asyncio.Queue[KeyActivityReport] = self.subscribe(
            KeyActivityReport
        )
        self._temperature_queue: asyncio.Queue[TemperatureReport] = self.subscribe(
            TemperatureReport
        )

        asyncio.create_task(self._handle_key_activity())
        asyncio.create_task(self._handle_temperature())

        self._connection_made.set_result(None)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self._running = False
        if exc:
            raise ConnectionError("Connection lost") from exc

    def close(self) -> None:
        self._running = False
        if self._transport:
            self._transport.close()

    def data_received(self, data: bytes) -> None:
        self._buffer += data

        packet, buff = parse_packet(self._buffer)
        self._buffer = buff

        while packet:
            self._packet_received(packet)
            packet, buff = parse_packet(self._buffer)
            self._buffer = buff

    def _packet_received(self, packet: Packet) -> None:
        res = Response.from_packet(packet)
        if type(res) in self._queues:
            for q in self._queues[type(res)]:
                q.put_nowait(res)

    def subscribe[R](self, cls: Type[R]) -> asyncio.Queue[R]:
        q: asyncio.Queue[R] = asyncio.Queue()
        self._queues[cast(Type[Response], cls)].append(cast(asyncio.Queue[Response], q))
        return q

    def unsubscribe[R](self, cls: Type[R], q: asyncio.Queue[R]) -> None:
        key = cast(Type[Response], cls)
        self._queues[key] = cast(
            List[asyncio.Queue[Response]],
            [q_ for q_ in self._queues[key] if q_ != cast(asyncio.Queue[Response], q)],
        )

    async def expect[R](self, cls: Type[R]) -> R:
        q = self.subscribe(cls)
        res = await q.get()
        self.unsubscribe(cls, q)
        return res

    def send_command(self, command: Command) -> None:
        self.send_packet(command.to_packet())

    def send_packet(self, packet: Packet) -> None:
        if not self._transport:
            raise ConnectionError("Must be connected to send data")
        buff = serialize_packet(packet)
        self._transport.write(buff)

    async def ping(self, payload: bytes) -> Pong:
        self.send_command(Ping(payload))
        return await self.expect(Pong)

    async def versions(self) -> Versions:
        self.send_command(GetVersions())
        return await self.expect(Versions)

    def write_user_flash(self) -> None:
        raise NotImplementedError("write_user_flash")

    def read_user_flash(self) -> None:
        raise NotImplementedError("read_user_flash")

    def store_boot_state(self) -> None:
        raise NotImplementedError("store_boot_state")

    def power_command(self) -> None:
        raise NotImplementedError("power_command")

    def clear(self) -> None:
        raise NotImplementedError("clear")

    async def set_line_1(self, line: str) -> SetLine1Response:
        self.send_command(SetLine1(line, self.device))
        return await self.expect(SetLine1Response)

    async def set_line_2(self, line: str) -> SetLine2Response:
        self.send_command(SetLine2(line, self.device))
        return await self.expect(SetLine2Response)

    def set_special_char_data(self) -> None:
        raise NotImplementedError("set_special_char_data")

    def poke(self) -> None:
        raise NotImplementedError("poke")

    def set_cursor_pos(self) -> None:
        raise NotImplementedError("set_cursor_pos")

    def set_cursor_style(self) -> None:
        raise NotImplementedError("set_cursor_style")

    def set_contrast(self) -> None:
        raise NotImplementedError("set_contrast")

    def set_backlight(self) -> None:
        raise NotImplementedError("set_backlight")

    def read_dow_info(self) -> None:
        raise NotImplementedError("read_dow_info")

    def setup_temp_report(self) -> None:
        raise NotImplementedError("setup_temp_report")

    def dow_txn(self) -> None:
        raise NotImplementedError("dow_txn")

    def setup_temp_display(self) -> None:
        raise NotImplementedError("setup_temp_display")

    def raw_cmd(self) -> None:
        raise NotImplementedError("raw_cmd")

    def config_key_report(self) -> None:
        raise NotImplementedError("config_key_report")

    def poll_keypad(self) -> None:
        raise NotImplementedError("poll_keypad")

    def set_atx_switch(self) -> None:
        raise NotImplementedError("set_atx_switch")

    def config_watchdog(self) -> None:
        raise NotImplementedError("config_watchdog")

    async def read_status(self) -> DeviceStatus:
        self.send_command(ReadStatus())
        res = await self.expect(StatusResponse)
        return self.device.status(res.data)

    def send_data(self) -> None:
        raise NotImplementedError("send_data")

    def set_baud(self) -> None:
        raise NotImplementedError("set_baud")

    def config_gpio(self) -> None:
        raise NotImplementedError("config_gpio")

    def read_gpio(self) -> None:
        raise NotImplementedError("read_gpio")

    async def _handle_key_activity(self: Self) -> None:
        while True:
            if not self._running:
                return

            report = await self._key_activity_queue.get()
            await self._report_handler.on_key_activity(report)

    async def _handle_temperature(self: Self) -> None:
        while True:
            if not self._running:
                return

            report = await self._temperature_queue.get()
            await self._report_handler.on_temperature(report)


async def create_connection(
    port: str,
    model: str = "CFA533",
    hardware_rev: str = "h1.4",
    firmware_rev: str = "u1v2",
    device: Optional[Device] = None,
    report_handler: Optional[ReportHandler] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    baudrate: int = 19200,
    # TODO: There are hints that these are configurable??
    bytesize=EIGHTBITS,
    parity=PARITY_NONE,
    stopbits=STOPBITS_ONE,
) -> Client:
    _loop = loop if loop else asyncio.get_running_loop()

    if not device:
        device = DEVICES[model][hardware_rev][firmware_rev]

    if not report_handler:
        report_handler = NoopReportHandler()

    _, client = await create_serial_connection(
        _loop,
        lambda: Client(device=device, report_handler=report_handler, loop=_loop),
        port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
    )

    await client._connection_made

    return client
