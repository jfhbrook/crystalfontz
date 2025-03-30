import asyncio
import logging
from typing import List, Optional, Self, Tuple

from sdbus import (  # pyright: ignore [reportMissingModuleSource];; dbus_signal_async,
    dbus_method_async,
    dbus_property_async,
    DbusInterfaceCommonAsync,
    DbusUnprivilegedFlag,
)

from crystalfontz.client import Client, create_connection
from crystalfontz.config import Config
from crystalfontz.dbus.config import ConfigStruct
from crystalfontz.dbus.map import (
    BaudRateM,
    ConfigM,
    DeviceM,
    DowDeviceInformationM,
    DowTransactionM,
    DowTransactionResultM,
    LcdMemoryM,
    OkM,
    PingM,
    PongM,
    ReadDowDeviceInformationM,
    ReadLcdMemoryM,
    SendCommandToLcdControllerM,
    SetBacklightM,
    SetContrastM,
    SetCursorPositionM,
    SetCursorStyleM,
    SetLineM,
    SetupLiveTemperatureDisplayM,
    SetupTemperatureReportingM,
    SimpleCommandM,
    UserFlashAreaReadM,
    VersionsM,
    WriteUserFlashAreaM,
)
from crystalfontz.error import ConnectionError

Ok = bool

logger = logging.getLogger(__name__)

DBUS_NAME = "org.jfhbrook.crystalfontz"


async def load_client(config_file: Optional[str]) -> Client:
    config: Config = Config.from_file(config_file)

    client = await create_connection(config.port)

    return client


class DbusInterface(  # type: ignore
    DbusInterfaceCommonAsync, interface_name=DBUS_NAME  # type: ignore
):
    """
    A DBus interface for controlling the Crystalfontz device.
    """

    def __init__(self: Self, client: Client, config_file: Optional[str] = None) -> None:
        super().__init__()
        self._config: Config = Config.from_file(config_file)
        self.client: Client = client
        self._client_lock: asyncio.Lock = asyncio.Lock()

    @dbus_property_async(ConfigM.t)
    def config(self: Self) -> ConfigStruct:
        """
        The DBus service's currently loaded configuration.
        """

        return ConfigM.dump(self._config)

    async def close(self: Self) -> None:
        """
        Unsubscribe from events and close the client.
        """

        async with self._client_lock:
            self.client.close()
            await self.client.closed

    @property
    def closed(self: Self) -> asyncio.Future:
        """
        A Future that resolves when the client is closed.
        """

        return self.client.closed

    @dbus_method_async(PingM.t, PongM.t, flags=DbusUnprivilegedFlag)
    async def ping(
        self: Self,
        payload: List[int],
        timeout: float,
        retry_times: int,
    ) -> List[int]:
        pong = await self.client.ping(*PingM.load(payload, timeout, retry_times))
        return PongM.dump(pong)

    @dbus_method_async(SimpleCommandM.t, OkM.t, flags=DbusUnprivilegedFlag)
    async def test_connection(self: Self, timeout: float, retry_times: int) -> Ok:
        try:
            await self.client.test_connection(
                *SimpleCommandM.load(timeout, retry_times)
            )
        except ConnectionError:
            return False
        else:
            return True

    # TODO: Should receive timeout and retry_times
    @dbus_method_async("", BaudRateM.t, flags=DbusUnprivilegedFlag)
    async def detect_baud_rate(self: Self) -> int:
        # Detect the baud rate, as you do
        await self.client.detect_baud_rate()

        # Save to the loaded config
        self._config.baud_rate = self.client.baud_rate

        # Return the new baud rate
        return self.client.baud_rate

    @dbus_method_async(SimpleCommandM.t, VersionsM.t, flags=DbusUnprivilegedFlag)
    async def versions(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> Tuple[str, str, str]:
        versions = await self.client.versions(
            *SimpleCommandM.load(timeout, retry_times)
        )
        return VersionsM.dump(versions)

    @dbus_method_async(SimpleCommandM.t, DeviceM.t, flags=DbusUnprivilegedFlag)
    async def detect_device(
        self: Self, timeout: float, retry_times: int
    ) -> Tuple[str, str, str]:
        await self.client.detect_device(*SimpleCommandM.load(timeout, retry_times))
        return DeviceM.dump(self.client.device)

    @dbus_method_async(WriteUserFlashAreaM.t, "", flags=DbusUnprivilegedFlag)
    async def write_user_flash_area(
        self: Self, data: bytes, timeout: float, retry_times: int
    ) -> None:
        await self.client.write_user_flash_area(
            *WriteUserFlashAreaM.load(data, timeout, retry_times)
        )

    @dbus_method_async(
        SimpleCommandM.t, UserFlashAreaReadM.t, flags=DbusUnprivilegedFlag
    )
    async def read_user_flash_area(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> bytes:
        res = await self.client.read_user_flash_area(
            *SimpleCommandM.load(timeout, retry_times)
        )
        return UserFlashAreaReadM.dump(res)

    @dbus_method_async(SimpleCommandM.t, "", flags=DbusUnprivilegedFlag)
    async def store_boot_state(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.store_boot_state(*SimpleCommandM.load(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, "", flags=DbusUnprivilegedFlag)
    async def reboot_lcd(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.reboot_lcd(*SimpleCommandM.load(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, "", flags=DbusUnprivilegedFlag)
    async def reset_host(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.reset_host(*SimpleCommandM.load(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, "", flags=DbusUnprivilegedFlag)
    async def shutdown_host(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.shutdown_host(*SimpleCommandM.load(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, "", flags=DbusUnprivilegedFlag)
    async def clear_screen(
        self: Self,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.clear_screen(*SimpleCommandM.load(timeout, retry_times))

    @dbus_method_async(SetLineM.t, "", flags=DbusUnprivilegedFlag)
    async def set_line_1(
        self: Self,
        line: bytes,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.set_line_1(*SetLineM.load(line, timeout, retry_times))

    @dbus_method_async(SetLineM.t, "", flags=DbusUnprivilegedFlag)
    async def set_line_2(
        self: Self,
        line: bytes,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.set_line_2(*SetLineM.load(line, timeout, retry_times))

    @dbus_method_async(ReadLcdMemoryM.t, LcdMemoryM.t, flags=DbusUnprivilegedFlag)
    async def read_lcd_memory(
        self: Self,
        address: int,
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, List[int]]:
        memory = await self.client.read_lcd_memory(
            *ReadLcdMemoryM.load(address, timeout, retry_times)
        )

        return LcdMemoryM.dump(memory)

    @dbus_method_async(SetCursorPositionM.t, "", flags=DbusUnprivilegedFlag)
    async def set_cursor_position(
        self: Self,
        row: int,
        column: int,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.set_cursor_position(
            *SetCursorPositionM.load(row, column, timeout, retry_times)
        )

    @dbus_method_async(SetCursorStyleM.t, "", flags=DbusUnprivilegedFlag)
    async def set_cursor_style(
        self: Self,
        style: int,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.set_cursor_style(
            *SetCursorStyleM.load(style, timeout, retry_times)
        )

    @dbus_method_async(SetContrastM.t, "", flags=DbusUnprivilegedFlag)
    async def set_contrast(
        self: Self,
        contrast: float,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.set_contrast(
            *SetContrastM.load(contrast, timeout, retry_times)
        )

    @dbus_method_async(SetBacklightM.t, "", flags=DbusUnprivilegedFlag)
    async def set_backlight(
        self: Self,
        lcd_brightness: float,
        keypad_brightness: float,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.set_backlight(
            *SetBacklightM.load(lcd_brightness, keypad_brightness, timeout, retry_times)
        )

    @dbus_method_async(
        ReadDowDeviceInformationM.t, DowDeviceInformationM.t, flags=DbusUnprivilegedFlag
    )
    async def read_dow_device_information(
        self: Self,
        index: int,
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, List[int]]:
        info = await self.client.read_dow_device_information(
            *ReadDowDeviceInformationM.load(index, timeout, retry_times)
        )

        return DowDeviceInformationM.dump(info)

    @dbus_method_async(SetupTemperatureReportingM.t, "", flags=DbusUnprivilegedFlag)
    async def setup_temperature_reporting(
        self: Self,
        enabled: List[int],
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.setup_temperature_reporting(
            *SetupTemperatureReportingM.load(enabled, timeout, retry_times)
        )

    @dbus_method_async(
        DowTransactionM.t, DowTransactionResultM.t, flags=DbusUnprivilegedFlag
    )
    async def dow_transaction(
        self: Self,
        index: int,
        bytes_to_read: int,
        data_to_write: List[int],
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, List[int], int]:
        res = await self.client.dow_transaction(
            *DowTransactionM.load(
                index, bytes_to_read, data_to_write, timeout, retry_times
            )
        )

        return DowTransactionResultM.dump(res)

    @dbus_method_async(SetupLiveTemperatureDisplayM.t, "", flags=DbusUnprivilegedFlag)
    async def setup_live_temperature_display(
        self: Self,
        slot: int,
        item: Tuple[int, int, int, int, bool],
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.setup_live_temperature_display(
            *SetupLiveTemperatureDisplayM.load(slot, item, timeout, retry_times)
        )

    @dbus_method_async(SendCommandToLcdControllerM.t, "", flags=DbusUnprivilegedFlag)
    async def send_command_to_lcd_controller(
        self: Self,
        location: bool,
        data: int,
        timeout: float,
        retry_times: int,
    ) -> None:
        await self.client.send_command_to_lcd_controller(
            *SendCommandToLcdControllerM.load(location, data, timeout, retry_times)
        )
