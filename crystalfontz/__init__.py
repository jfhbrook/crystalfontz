from typing import List

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate, FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.client import Client, connection, create_connection
from crystalfontz.command import Command
from crystalfontz.config import Config
from crystalfontz.cursor import CursorStyle
from crystalfontz.device import Device, DeviceStatus
from crystalfontz.effects import Effect, Marquee, Screensaver
from crystalfontz.error import (
    ConnectionError,
    CrystalfontzError,
    DecodeError,
    DeviceError,
    DeviceLookupError,
    EncodeError,
    UnknownResponseError,
)
from crystalfontz.gpio import (
    GPIO_HIGH,
    GPIO_LOW,
    GpioDriveMode,
    GpioFunction,
    GpioSettings,
    GpioState,
)
from crystalfontz.keys import (
    KeyActivity,
    KeyState,
    KeyStates,
    KP_DOWN,
    KP_ENTER,
    KP_EXIT,
    KP_LEFT,
    KP_RIGHT,
    KP_UP,
)
from crystalfontz.lcd import LcdRegister
from crystalfontz.packet import Packet
from crystalfontz.protocol import ClientProtocol
from crystalfontz.receiver import Receiver
from crystalfontz.report import LoggingReportHandler, NoopReportHandler, ReportHandler
from crystalfontz.response import (
    AtxPowerSwitchFunctionalitySet,
    BacklightSet,
    BaudRateSet,
    BootStateStored,
    ClearedScreen,
    CommandSentToLcdController,
    ContrastSet,
    CursorPositionSet,
    CursorStyleSet,
    DataSent,
    KeyActivityReport,
    KeypadPolled,
    KeyReportingConfigured,
    LcdMemory,
    Line1Set,
    Line2Set,
    LiveTemperatureDisplaySetUp,
    Pong,
    PowerResponse,
    RawResponse,
    Response,
    SpecialCharacterDataSet,
    StatusRead,
    TemperatureReport,
    TemperatureReportingSetUp,
    UserFlashAreaRead,
    UserFlashAreaWritten,
    Versions,
    WatchdogConfigured,
)
from crystalfontz.temperature import TemperatureDisplayItem, TemperatureUnit
from crystalfontz.watchdog import WATCHDOG_DISABLED

__all__: List[str] = [
    "AtxPowerSwitchFunction",
    "AtxPowerSwitchFunctionalitySet",
    "AtxPowerSwitchFunctionalitySettings",
    "BacklightSet",
    "BaudRate",
    "BaudRateSet",
    "BootStateStored",
    "ClearedScreen",
    "Client",
    "ClientProtocol",
    "Command",
    "CommandSentToLcdController",
    "Config",
    "connection",
    "ConnectionError",
    "ContrastSet",
    "create_connection",
    "CrystalfontzError",
    "CursorPositionSet",
    "CursorStyle",
    "CursorStyleSet",
    "DataSent",
    "DecodeError",
    "Device",
    "DeviceError",
    "DeviceLookupError",
    "DeviceStatus",
    "Effect",
    "EncodeError",
    "FAST_BAUD_RATE",
    "GPIO_HIGH",
    "GPIO_LOW",
    "GpioDriveMode",
    "GpioFunction",
    "GpioSettings",
    "GpioState",
    "KP_DOWN",
    "KP_ENTER",
    "KP_EXIT",
    "KP_LEFT",
    "KP_RIGHT",
    "KP_UP",
    "KeyActivity",
    "KeyActivityReport",
    "KeyReportingConfigured",
    "KeyState",
    "KeyStates",
    "KeypadPolled",
    "LcdRegister",
    "Line1Set",
    "Line2Set",
    "LiveTemperatureDisplaySetUp",
    "LoggingReportHandler",
    "Marquee",
    "NoopReportHandler",
    "Packet",
    "LcdMemory",
    "Pong",
    "PowerResponse",
    "RawResponse",
    "Receiver",
    "ReportHandler",
    "Response",
    "SLOW_BAUD_RATE",
    "Screensaver",
    "SpecialCharacterDataSet",
    "StatusRead",
    "TemperatureDisplayItem",
    "TemperatureReport",
    "TemperatureReportingSetUp",
    "TemperatureUnit",
    "UnknownResponseError",
    "UserFlashAreaRead",
    "UserFlashAreaWritten",
    "Versions",
    "WATCHDOG_DISABLED",
    "WatchdogConfigured",
]
