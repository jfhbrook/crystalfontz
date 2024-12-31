import asyncio
from typing import Any, Optional

from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport

from crystalfontz.command import Command
from crystalfontz.error import ConnectionError
from crystalfontz.packet import Packet, parse_packet, serialize_packet
from crystalfontz.report import Report


class Client(asyncio.Protocol):
    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        _loop = loop if loop else asyncio.get_running_loop()

        self._buffer: bytes = b""
        self._loop: asyncio.AbstractEventLoop = _loop
        self._connection_made: asyncio.Future[None] = self._loop.create_future()
        self.reports: asyncio.Queue[Report] = asyncio.Queue()

    def connection_made(self, transport) -> None:
        self.transport = transport

        if not isinstance(transport, SerialTransport):
            raise ConnectionError("Transport is not a SerialTransport")

        self._transport = transport
        self._connection_made.set_result(None)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            raise ConnectionError("Connection lost") from exc

    def close(self) -> None:
        if not self._transport:
            raise ConnectionError("Can not close uninitialized connection")
        self._transport.close()

    def data_received(self, data: bytes) -> None:
        self._buffer += data

        packet, buff = parse_packet(self._buffer)
        self._buffer = buff

        while packet:
            self.reports.put_nowait(Report.from_packet(packet))
            packet, buff = parse_packet(self._buffer)
            self._buffer = buff

    def send_command(self, command: Command) -> None:
        self.send_packet(command.to_packet())

    def send_packet(self, packet: Packet) -> None:
        buff = serialize_packet(packet)
        self._transport.write(buff)

    def ping(self) -> None:
        raise NotImplementedError("ping")

    def versions(self) -> str:
        raise NotImplementedError("versions")

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

    def set_l1(self, line: str) -> None:
        raise NotImplementedError("set_l1")

    def set_l2(self, line: str) -> None:
        raise NotImplementedError("set_l2")

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

    def read_status(self) -> None:
        raise NotImplementedError("read_status")

    def send_data(self) -> None:
        raise NotImplementedError("send_data")

    def set_baud(self) -> None:
        raise NotImplementedError("set_baud")

    def config_gpio(self) -> None:
        raise NotImplementedError("config_gpio")

    def read_gpio(self) -> None:
        raise NotImplementedError("read_gpio")


async def create_connection(
    port: str,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    baudrate: int = 19200,
    # TODO: There are hints that these are configurable??
    bytesize=EIGHTBITS,
    parity=PARITY_NONE,
    stopbits=STOPBITS_ONE,
) -> Client:
    _loop = loop if loop else asyncio.get_running_loop()

    _, client = await create_serial_connection(
        _loop,
        lambda: Client(_loop),
        port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
    )

    await client._connection_made

    return client
