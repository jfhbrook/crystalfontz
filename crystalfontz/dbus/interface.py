import asyncio
import logging
from typing import List, Optional, Self

from sdbus import (  # pyright: ignore [reportMissingModuleSource];; dbus_signal_async,
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
    DbusInterfaceCommonAsync,
    DbusUnprivilegedFlag,
)

from crystalfontz.client import Client, create_connection
from crystalfontz.config import Config
from crystalfontz.dbus.domain.atx import AtxPowerSwitchFunctionalitySettingsT
from crystalfontz.dbus.domain.base import (
    AddressT,
    ByteT,
    IndexT,
    NoneM,
    OkM,
    PositionT,
    RetryTimesT,
    TimeoutT,
)
from crystalfontz.dbus.domain.baud import BaudRateM, BaudRateT
from crystalfontz.dbus.domain.character import SpecialCharacterT
from crystalfontz.dbus.domain.command import (
    ConfigureKeyReportingM,
    ConfigureWatchdogM,
    DowTransactionM,
    PingM,
    ReadDowDeviceInformationM,
    ReadGpioM,
    ReadLcdMemoryM,
    SendCommandToLcdControllerM,
    SendDataM,
    SetAtxPowerSwitchFunctionalityM,
    SetBacklightM,
    SetBaudRateM,
    SetContrastM,
    SetCursorPositionM,
    SetCursorStyleM,
    SetGpioM,
    SetLineM,
    SetSpecialCharacterDataM,
    SetSpecialCharacterEncodingM,
    SetupLiveTemperatureDisplayM,
    SetupTemperatureReportingM,
    SimpleCommandM,
    WriteUserFlashAreaM,
)
from crystalfontz.dbus.domain.config import ConfigM, ConfigT
from crystalfontz.dbus.domain.device import (
    DeviceM,
    DeviceStatusM,
    DeviceStatusT,
    DeviceT,
)
from crystalfontz.dbus.domain.gpio import OptGpioSettingsT
from crystalfontz.dbus.domain.keys import KeyPressT
from crystalfontz.dbus.domain.lcd import LcdRegisterT
from crystalfontz.dbus.domain.response import (
    DowDeviceInformationM,
    DowDeviceInformationT,
    DowTransactionResultM,
    DowTransactionResultT,
    GpioReadM,
    GpioReadT,
    KeyActivityReportM,
    KeyActivityReportT,
    KeypadPolledM,
    KeypadPolledT,
    LcdMemoryM,
    LcdMemoryT,
    PongM,
    PongT,
    TemperatureReportM,
    TemperatureReportT,
    UserFlashAreaReadM,
    UserFlashAreaReadT,
    VersionsM,
    VersionsT,
)
from crystalfontz.dbus.domain.temperature import TemperatureDisplayItemT
from crystalfontz.dbus.report import DbusReportHandler
from crystalfontz.error import ConnectionError

Ok = bool

logger = logging.getLogger(__name__)

DBUS_NAME = "org.jfhbrook.crystalfontz"


async def load_client(
    report_handler: Optional[DbusReportHandler], config_file: Optional[str]
) -> Client:
    config: Config = Config.from_file(config_file)

    client = await create_connection(config.port, report_handler=report_handler)

    return client


class DbusInterface(  # type: ignore
    DbusInterfaceCommonAsync, interface_name=DBUS_NAME  # type: ignore
):
    """
    A DBus interface for controlling the Crystalfontz device.
    """

    def __init__(
        self: Self,
        client: Client,
        report_handler: Optional[DbusReportHandler] = None,
        config_file: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._config: Config = Config.from_file(config_file)
        self.client: Client = client
        self._client_lock: asyncio.Lock = asyncio.Lock()
        self.report_handler = report_handler

        if self.report_handler:
            self.report_handler.iface = self

    @dbus_property_async(ConfigM.t)
    def config(self: Self) -> ConfigT:
        """
        The DBus service's currently loaded configuration.
        """

        return ConfigM.pack(self._config)

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
        payload: bytes,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> PongT:
        """
        0 (0x00): Ping Command

        The device will return the Ping Command to the host.
        """

        pong = await self.client.ping(*PingM.unpack(payload, timeout, retry_times))
        return PongM.pack(pong)

    @dbus_method_async(SimpleCommandM.t, OkM.t, flags=DbusUnprivilegedFlag)
    async def test_connection(
        self: Self, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Ok:
        """
        Test the connection by sending a ping and checking that the response matches.
        """

        try:
            await self.client.test_connection(
                *SimpleCommandM.unpack(timeout, retry_times)
            )
        except ConnectionError:
            return False
        else:
            return True

    @dbus_method_async(SimpleCommandM.t, BaudRateM.t)
    async def detect_baud_rate(
        self: Self, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> BaudRateT:
        """
        Detect the device's configured baud rate by testing the connection at each
        potential baud setting.

        This is a privileged API, as it modifies the baud rate used by the both the
        client and the device.
        """

        # Detect the baud rate, as you do
        await self.client.detect_baud_rate(*SimpleCommandM.unpack(timeout, retry_times))

        # Save to the loaded config
        self._config.baud_rate = self.client.baud_rate

        # Return the new baud rate
        return self.client.baud_rate

    @dbus_method_async(SimpleCommandM.t, VersionsM.t, flags=DbusUnprivilegedFlag)
    async def versions(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> VersionsT:
        """
        1 (0x01): Get Hardware & Firmware Version

        The device will return the hardware and firmware version information to the
        host.
        """

        versions = await self.client.versions(
            *SimpleCommandM.unpack(timeout, retry_times)
        )
        return VersionsM.pack(versions)

    @dbus_method_async(SimpleCommandM.t, DeviceM.t)
    async def detect_device(self: Self, timeout: TimeoutT, retry_times: int) -> DeviceT:
        """
        Get model, hardware and firmware versions from the device, then configure the
        client to use that device. This is useful if you don't know a priori what
        device you're using.

        This is a privileged API, as it modifies the device settings for the client.
        """

        await self.client.detect_device(*SimpleCommandM.unpack(timeout, retry_times))
        return DeviceM.pack(self.client.device)

    @dbus_method_async(WriteUserFlashAreaM.t, NoneM.t)
    async def write_user_flash_area(
        self: Self, data: bytes, timeout: TimeoutT, retry_times: int
    ) -> None:
        """
        2 (0x02): Write User Flash Area

        The CFA533 reserves 16 bytes of nonvolatile memory for arbitrary use by the
        host. This memory can be used to store a serial number, IP address, gateway
        address, netmask, or any other data required. All 16 bytes must be supplied.

        This is a privileged API, as it modifies the state of the device.
        """

        await self.client.write_user_flash_area(
            *WriteUserFlashAreaM.unpack(data, timeout, retry_times)
        )

    @dbus_method_async(
        SimpleCommandM.t, UserFlashAreaReadM.t, flags=DbusUnprivilegedFlag
    )
    async def read_user_flash_area(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> UserFlashAreaReadT:
        """
        3 (0x03): Read User Flash Area

        This command will read the User Flash Area and return the data to the host.
        For more information, review the documentation for
        `client.write_user_flash_area`.
        """

        res = await self.client.read_user_flash_area(
            *SimpleCommandM.unpack(timeout, retry_times)
        )
        return UserFlashAreaReadM.pack(res)

    @dbus_method_async(SimpleCommandM.t, NoneM.t)
    async def store_boot_state(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        4 (0x04): Store Current State as Boot State

        The device loads its power-up configuration from nonvolatile memory when
        power is applied. The device is configured at the factory to display a
        "welcome" screen when power is applied. This command can be used to customize
        the "welcome" screen, as well as the following items:

        - Characters shown on LCD
        - Special character font definitions
        - Cursor position
        - Cursor style
        - Contrast setting
        - LCD backlight setting
        - Settings of any "live" displays, such as temperature display
        - Key press and release masks
        - ATX function enable and pulse length settings
        - Baud rate
        - GPIO settings

        You cannot store the temperature reporting (although the live display of
        temperatures can be saved). You cannot store the host watchdog. The host
        software should enable this item once the system is initialized and is ready
        to receive the data.

        This is a privileged API, as it modifies the state of the device.
        """

        await self.client.store_boot_state(*SimpleCommandM.unpack(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, NoneM.t)
    async def reboot_lcd(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        Reboot the device, using 5 (0x05): Reboot Device, Reset Host, or Power Off
        Host.

        Rebooting the device may be useful for testing the boot configuration. It may
        also be useful to re-enumerate the devices on the One-Wire bus.

        This is a privileged API, as it impacts the availability of the device.
        """

        await self.client.reboot_lcd(*SimpleCommandM.unpack(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, NoneM.t)
    async def reset_host(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        Reset the host, using 5 (0x05): Reboot Device, Reset Host, or Power Off Host.

        This command assumes the host's reset line is connected to GPIO[3]. For more
        information, review your device's datasheet.

        This is a privileged API, as it impacts the availability of the host.
        """

        await self.client.reset_host(*SimpleCommandM.unpack(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, NoneM.t)
    async def shutdown_host(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        Turn off the host's power, using 5 (0x05): Reboot Device, Reset Host, or Power
        Off Host.

        This command assumes the host's power control line is connected to GPIO[2].
        For more information, review your device's datasheet.

        This is a privileged API, as it impacts the availability of the host.
        """

        await self.client.shutdown_host(*SimpleCommandM.unpack(timeout, retry_times))

    @dbus_method_async(SimpleCommandM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def clear_screen(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        6 (0x06): Clear LCD Screen

        Sets the contents of the LCD screen DDRAM to '' = 0x20 = 32 and moves the
        cursor to the left-most column of the top line.
        """

        await self.client.clear_screen(*SimpleCommandM.unpack(timeout, retry_times))

    @dbus_method_async(SetLineM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def set_line_1(
        self: Self,
        line: bytes,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        7 (0x07): Set LCD Contents, Line 1

        Sets the center 16 characters displayed on the top line of the LCD screen.

        Please use this command only if you need backwards compatibility with older
        devices. For new applications, please use the more flexible command
        `client.send_data`.
        """

        await self.client.set_line_1(*SetLineM.unpack(line, timeout, retry_times))

    @dbus_method_async(SetLineM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def set_line_2(
        self: Self,
        line: bytes,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        8 (0x08): Set LCD Contents, Line 2

        Sets the center 16 characters displayed on the bottom line of the LCD screen.

        Please use this command only if you need backwards compatibility with older
        devices. For new applications, please use the more flexible command
        `client.send_data`.
        """

        await self.client.set_line_2(*SetLineM.unpack(line, timeout, retry_times))

    @dbus_method_async(SetSpecialCharacterDataM.t, NoneM.t)
    async def set_special_character_data(
        self: Self,
        index: IndexT,
        character: SpecialCharacterT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        9 (0x09): Set LCD Special Character Data

        Sets the font definition for one of the special characters (CGRAM).

        This is a privileged API, as it modifies the state of the device.
        """

        await self.client.send_command(
            *SetSpecialCharacterDataM.unpack(index, character, timeout, retry_times)
        )

    @dbus_method_async(SetSpecialCharacterEncodingM.t, NoneM.t)
    async def set_special_character_encoding(
        self: Self,
        character: str,
        index: IndexT,
    ) -> None:
        """
        Configure a unicode character to encode to the index of a given special
        character on CGRAM.

        This is a privileged API, as it modifies the configuration of the client.
        """

        self.client.device.character_rom.set_encoding(character, index)

    @dbus_method_async(ReadLcdMemoryM.t, LcdMemoryM.t, flags=DbusUnprivilegedFlag)
    async def read_lcd_memory(
        self: Self,
        address: AddressT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> LcdMemoryT:
        """
        10 (0x0A): Read 8 bytes of LCD Memory

        This command will return the contents of the LCD's DDRAM or CGRAM. This
        command is intended for debugging.
        """

        memory = await self.client.read_lcd_memory(
            *ReadLcdMemoryM.unpack(address, timeout, retry_times)
        )

        return LcdMemoryM.pack(memory)

    @dbus_method_async(SetCursorPositionM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def set_cursor_position(
        self: Self,
        row: int,
        column: int,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        11 (0x0B): Set LCD Cursor Position

        This command allows the cursor to be placed at the desired location on the
        device's LCD screen.
        """

        await self.client.set_cursor_position(
            *SetCursorPositionM.unpack(row, column, timeout, retry_times)
        )

    @dbus_method_async(SetCursorStyleM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def set_cursor_style(
        self: Self,
        style: int,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        12 (0x0C): Set LCD Cursor Style

        This command allows you to select among four hardware generated cursor
        options.
        """

        await self.client.set_cursor_style(
            *SetCursorStyleM.unpack(style, timeout, retry_times)
        )

    @dbus_method_async(SetContrastM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def set_contrast(
        self: Self,
        contrast: float,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        13 (0x0D): Set LCD Contrast

        This command sets the contrast or vertical viewing angle of the display.
        """

        await self.client.set_contrast(
            *SetContrastM.unpack(contrast, timeout, retry_times)
        )

    @dbus_method_async(SetBacklightM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def set_backlight(
        self: Self,
        lcd_brightness: float,
        keypad_brightness: float,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        14 (0x0E): Set LCD & Keypad Backlight

        This command sets the brightness of the LCD and keypad backlights.
        """

        await self.client.set_backlight(
            *SetBacklightM.unpack(
                lcd_brightness, keypad_brightness, timeout, retry_times
            )
        )

    @dbus_method_async(
        ReadDowDeviceInformationM.t, DowDeviceInformationM.t, flags=DbusUnprivilegedFlag
    )
    async def read_dow_device_information(
        self: Self,
        index: int,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> DowDeviceInformationT:
        """
        18 (0x12): Read DOW Device Information

        When power is applied to the unit, it detects any devices connected to the
        Dallas Semiconductor One-Wire (DOW) bus and stores the device's information.
        This command will allow the host to read the device's information.

        Note: The GPIO pin used for DOW must not be configured as user GPIO. For more
        information, review your unit's datasheet.
        """

        info = await self.client.read_dow_device_information(
            *ReadDowDeviceInformationM.unpack(index, timeout, retry_times)
        )

        return DowDeviceInformationM.pack(info)

    @dbus_method_async(SetupTemperatureReportingM.t, NoneM.t)
    async def setup_temperature_reporting(
        self: Self,
        enabled: List[int],
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        19 (0x13): Set Up Temperature Reporting

        This command will configure the device to report the temperature information
        to the host every second.

        This is a privileged API, as it impacts the availability of temperature reports
        for other users.
        """

        await self.client.setup_temperature_reporting(
            *SetupTemperatureReportingM.unpack(enabled, timeout, retry_times)
        )

    @dbus_method_async(
        DowTransactionM.t, DowTransactionResultM.t, flags=DbusUnprivilegedFlag
    )
    async def dow_transaction(
        self: Self,
        index: int,
        bytes_to_read: int,
        data_to_write: bytes,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> DowTransactionResultT:
        """
        20 (0x14): Arbitrary DOW Transaction

        The unit can function as an RS-232 to Dallas 1-Wire bridge. The unit can
        send up to 15 bytes and receive up to 14 bytes. This will be sufficient for
        many devices, but some devices require larger transactions and cannot by fully
        used with the unit.

        For more information, review your unit's datasheet.
        """

        res = await self.client.dow_transaction(
            *DowTransactionM.unpack(
                index, bytes_to_read, data_to_write, timeout, retry_times
            )
        )

        return DowTransactionResultM.pack(res)

    @dbus_method_async(
        SetupLiveTemperatureDisplayM.t, NoneM.t, flags=DbusUnprivilegedFlag
    )
    async def setup_live_temperature_display(
        self: Self,
        slot: int,
        item: TemperatureDisplayItemT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        21 (0x15): Set Up Live Temperature Display

        You can configure the device to automatically update a portion of the LCD with
        a "live" temperature reading. Once the display is configured using this
        command, the device will continue to display the live reading on the LCD
        without host intervention.
        """

        await self.client.setup_live_temperature_display(
            *SetupLiveTemperatureDisplayM.unpack(slot, item, timeout, retry_times)
        )

    @dbus_method_async(
        SendCommandToLcdControllerM.t, NoneM.t, flags=DbusUnprivilegedFlag
    )
    async def send_command_to_lcd_controller(
        self: Self,
        location: LcdRegisterT,
        data: ByteT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        22 (0x16): Send Command Directly to the LCD Controller

        The controller on the CFA533 is HD44780 compatible. Generally, you will not
        need low-level access to the LCD controller but some arcane functions of the
        HD44780 are not exposed by the CFA533's command set. This command allows you
        to access the CFA533's LCD controller directly.
        """

        await self.client.send_command_to_lcd_controller(
            *SendCommandToLcdControllerM.unpack(location, data, timeout, retry_times)
        )

    @dbus_method_async(ConfigureKeyReportingM.t, NoneM.t)
    async def configure_key_reporting(
        self: Self,
        when_pressed: List[KeyPressT],
        when_released: List[KeyPressT],
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        23 (0x17): Configure Key Reporting


        By default, the device reports any key event to the host. This command allows
        the key events to be enabled or disabled on an individual basis.

        This is a privileged API, as it impacts the availability of key reports for
        other users.
        """

        await self.client.configure_key_reporting(
            *ConfigureKeyReportingM.unpack(
                when_pressed, when_released, timeout, retry_times
            )
        )

    @dbus_method_async(SimpleCommandM.t, KeypadPolledM.t, flags=DbusUnprivilegedFlag)
    async def poll_keypad(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> KeypadPolledT:
        """
        24 (0x18): Read Keypad, Polled Mode

        In some situations, it may be convenient for the host to poll the device for
        key activity. This command allows the host to detect which keys are currently
        pressed, which keys have been pressed since the last poll, and which keys have
        been released since the last poll.
        """

        polled = await self.client.poll_keypad(
            *SimpleCommandM.unpack(timeout, retry_times)
        )

        return KeypadPolledM.pack(polled)

    @dbus_method_async(SetAtxPowerSwitchFunctionalityM.t, NoneM.t)
    async def set_atx_power_switch_functionality(
        self: Self,
        settings: AtxPowerSwitchFunctionalitySettingsT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        28 (0x1C): Set ATX Power Switch Functionality

        The combination of this device with the Crystalfontz WR-PWR-Y14 cable can
        be used to replace the function of the power and reset switches in a standard
        ATX-compatible system.

        This functionality comes with a number of caveats. Please review your device's
        datasheet for more information.

        This is a privileged API, as changing these settings can impact the availability
        of the device.
        """

        await self.client.set_atx_power_switch_functionality(
            *SetAtxPowerSwitchFunctionalityM.unpack(settings, timeout, retry_times)
        )

    @dbus_method_async(ConfigureWatchdogM.t, NoneM.t)
    async def configure_watchdog(
        self: Self,
        timeout_seconds: ByteT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        29 (0x1D): Enable/Disable and Reset the Watchdog

        Some high-availability systems use hardware watchdog timers to ensure that
        a software or hardware failure does not result in an extended system outage.
        Once the host system has booted, a system monitor program is started. The
        system monitor program would enable the watchdog timer on the device. If the
        system monitor program fails to reset the device's watchdog timer, the device
        will reset the host system.

        The GPIO pins used for ATX control must not be configured as user GPIO. For
        more details, review your device's datasheet.

        This is a privileged API, as configuring the watchdog can impact the
        availability of the host.
        """

        await self.client.configure_watchdog(
            *ConfigureWatchdogM.unpack(timeout_seconds, timeout, retry_times)
        )

    @dbus_method_async(SimpleCommandM.t, DeviceStatusM.t, flags=DbusUnprivilegedFlag)
    async def read_status(
        self: Self,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> DeviceStatusT:
        """
        30 (0x1E): Read Reporting & Status

        This command can be used to verify the current items configured to report to
        the host, as well as some other miscellaneous status information. Please
        note that the information returned is not identical between devices, and may
        in fact vary between firmware versions of the same model. As such, the return
        value of this function is not type-safe.
        """

        status = await self.client.read_status(
            *SimpleCommandM.unpack(timeout, retry_times)
        )

        return DeviceStatusM.pack(status, self.client.device)

    @dbus_method_async(SendDataM.t, NoneM.t, flags=DbusUnprivilegedFlag)
    async def send_data(
        self: Self,
        row: PositionT,
        column: PositionT,
        data: bytes,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        31 (0x1F): Send Data to LCD

        This command allows data to be placed at any position on the LCD.
        """

        await self.client.send_data(
            *SendDataM.unpack(row, column, data, timeout, retry_times)
        )

    @dbus_method_async(SetBaudRateM.t, NoneM.t)
    async def set_baud_rate(
        self: Self,
        baud_rate: BaudRateT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        33 (0x21): Set Baud Rate

        This command will change the device's baud rate. This method sends the baud
        rate command, waits for a positive acknowledgement from the device at the old
        baud rate, and then switches to the new baud rate. The baud rate must be saved
        by a call to `client.store_boot_state` if you want the device to power up at
        the new baud rate.

        This is a privileged API, as changing the baud rate can impact the
        availability of the device.
        """

        await self.client.set_baud_rate(
            *SetBaudRateM.unpack(baud_rate, timeout, retry_times)
        )

    @dbus_method_async(SetGpioM.t, NoneM.t)
    async def set_gpio(
        self: Self,
        index: IndexT,
        output_state: ByteT,
        settings: OptGpioSettingsT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> None:
        """
        34 (0x22): Set or Set and Configure GPIO Pins

        The CFA533 (hardware versions 1.4 and up, firmware versions 1.9 and up) has
        five pins for user-definable general purpose input / output (GPIO). These pins
        are shared with the DOW and ATX functions. Be careful when you configure GPIO
        if you want to use the ATX or DOW at the same time.

        This functionality comes with many caveats. Please review the documentation in
        your device's datasheet.

        This is a privileged API, as changing these settings can impact the
        availability of the device.
        """

        await self.client.set_gpio(
            *SetGpioM.unpack(index, output_state, settings, timeout, retry_times)
        )

    @dbus_method_async(ReadGpioM.t, GpioReadM.t, flags=DbusUnprivilegedFlag)
    async def read_gpio(
        self: Self,
        index: IndexT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> GpioReadT:
        """
        35 (0x23): Read GPIO Pin Levels and Configuration State

        See method `client.set_gpio` for details on the GPIO architecture.

        This functionality comes with many caveats. Please review the documentation in
        your device's datasheet.
        """

        read = await self.client.read_gpio(
            *ReadGpioM.unpack(index, timeout, retry_times)
        )

        return GpioReadM.pack(read)

    @dbus_signal_async(KeyActivityReportM.t)
    def key_activity_reports(self: Self) -> KeyActivityReportT:
        """
        Listen for key activity reports.
        """

        raise NotImplementedError("key_activity_reports")

    @dbus_signal_async(TemperatureReportM.t)
    def temperature_reports(self: Self) -> TemperatureReportT:
        """
        Listen for temperature reports.
        """

        raise NotImplementedError("temperature_reports")


__all__ = ["DbusInterface", "DBUS_NAME"]
