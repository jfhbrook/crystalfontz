from typing import Optional, Self, Type

from crystalfontz.cursor import CursorStyle
from crystalfontz.dbus.domain import (
    CursorStyleM,
    KeypadBrightnessM,
    RetryTimesM,
    RetryTimesT,
    TimeoutM,
    TimeoutT,
    VersionsM,
)
from crystalfontz.dbus.interface import DbusInterface
from crystalfontz.device import Device, lookup_device
from crystalfontz.effects import EffectClient
from crystalfontz.response import (
    BacklightSet,
    ClearedScreen,
    ContrastSet,
    CursorPositionSet,
    CursorStyleSet,
    DataSent,
)


class DbusEffectClient(EffectClient):
    """
    A facade over a DBusClient for use by effects.
    """

    @classmethod
    async def load(
        cls: Type[Self],
        client: DbusInterface,
        timeout: TimeoutT = TimeoutM.none,
        retry_times: RetryTimesT = RetryTimesM.none,
    ) -> Self:
        """
        Given a DBusClient, create a DbusEffectClient.
        """

        versions = VersionsM.unpack(await client.versions(timeout, retry_times))
        device = lookup_device(
            versions.model, versions.hardware_rev, versions.firmware_rev
        )
        return cls(client, device)

    def __init__(self: Self, client: DbusInterface, device: Device) -> None:
        self.client: DbusInterface = client
        self.device: Device = device

    async def clear_screen(
        self: Self, timeout: Optional[float] = None, retry_times: Optional[int] = None
    ) -> ClearedScreen:
        await self.client.clear_screen(
            TimeoutM.pack(timeout), RetryTimesM.pack(retry_times)
        )
        return ClearedScreen()

    async def set_cursor_position(
        self: Self,
        row: int,
        column: int,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CursorPositionSet:
        await self.client.set_cursor_position(
            row, column, TimeoutM.pack(timeout), RetryTimesM.pack(retry_times)
        )
        return CursorPositionSet()

    async def set_cursor_style(
        self: Self,
        style: CursorStyle,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> CursorStyleSet:
        await self.client.set_cursor_style(
            CursorStyleM.pack(style),
            TimeoutM.pack(timeout),
            RetryTimesM.pack(retry_times),
        )
        return CursorStyleSet()

    async def set_contrast(
        self: Self,
        contrast: float,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> ContrastSet:
        await self.client.set_contrast(
            contrast, TimeoutM.pack(timeout), RetryTimesM.pack(retry_times)
        )
        return ContrastSet()

    async def set_backlight(
        self: Self,
        lcd_brightness: float,
        keypad_brightness: Optional[int] = None,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> BacklightSet:
        await self.client.set_backlight(
            lcd_brightness,
            KeypadBrightnessM.pack(keypad_brightness),
            TimeoutM.pack(timeout),
            RetryTimesM.pack(retry_times),
        )
        return BacklightSet()

    async def send_data(
        self: Self,
        row: int,
        column: int,
        data: str | bytes,
        timeout: Optional[float] = None,
        retry_times: Optional[int] = None,
    ) -> DataSent:
        await self.client.send_data(
            row,
            column,
            data.encode("utf-8") if isinstance(data, str) else data,
            TimeoutM.pack(timeout),
            RetryTimesM.pack(retry_times),
        )
        return DataSent()
