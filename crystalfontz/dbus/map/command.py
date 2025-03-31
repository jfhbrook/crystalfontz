from typing import ClassVar, List, Optional, Set, Tuple

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate
from crystalfontz.character import SpecialCharacter
from crystalfontz.cursor import CursorStyle
from crystalfontz.dbus.map.atx import AtxPowerSwitchFunctionalitySettingsM
from crystalfontz.dbus.map.base import (
    AddressM,
    array,
    ByteM,
    BytesM,
    IndexM,
    OptBytesM,
    OptFloatM,
    PositionM,
    RetryTimesM,
    t,
    TimeoutM,
)
from crystalfontz.dbus.map.baud import BaudRateM
from crystalfontz.dbus.map.character import SpecialCharacterM
from crystalfontz.dbus.map.cursor import CursorStyleM
from crystalfontz.dbus.map.lcd import LcdRegisterM
from crystalfontz.dbus.map.temperature import TemperatureDisplayItemM
from crystalfontz.lcd import LcdRegister
from crystalfontz.temperature import TemperatureDisplayItem


class SimpleCommandM:
    t: ClassVar[str] = t(TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        timeout: float, retry_times: int
    ) -> Tuple[Optional[float], Optional[int]]:
        return (TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class PingM:
    t: ClassVar[str] = t("y", TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        payload: List[int], timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (
            BytesM.unpack(payload),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class WriteUserFlashAreaM:
    t: ClassVar[str] = t("y", TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        data: bytes, timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (data, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetLineM:
    t: ClassVar[str] = t(BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        line: bytes, timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (line, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class ReadLcdMemoryM:
    t: ClassVar[str] = t(AddressM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        address: int, timeout: float, retry_times: int
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (address, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetCursorPositionM:
    t: ClassVar[str] = t(PositionM, PositionM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        row: int, column: int, timeout: float, retry_times: int
    ) -> Tuple[int, int, Optional[float], Optional[int]]:
        return (row, column, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetCursorStyleM:
    t: ClassVar[str] = t(CursorStyleM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        style: int, timeout: float, retry_times: int
    ) -> Tuple[CursorStyle, Optional[float], Optional[int]]:
        return (
            CursorStyleM.unpack(style),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetContrastM:
    t: ClassVar[str] = t("d", TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        contrast: float, timeout: float, retry_times: int
    ) -> Tuple[float, Optional[float], Optional[int]]:
        return (contrast, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetBacklightM:
    t: ClassVar[str] = t("dd", TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        lcd_brightness: float,
        keypad_brightness: float,
        timeout: float,
        retry_times: int,
    ) -> Tuple[float, Optional[float], Optional[float], Optional[int]]:
        return (
            lcd_brightness,
            OptFloatM.unpack(keypad_brightness),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class ReadDowDeviceInformationM:
    t: ClassVar[str] = t(IndexM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: int, timeout: float, retry_times: int
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (index, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetupTemperatureReportingM:
    t: ClassVar[str] = t(array("q"), TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        enabled: List[int], timeout: float, retry_times: int
    ) -> Tuple[List[int], Optional[float], Optional[int]]:
        return (enabled, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class DowTransactionM:
    t: ClassVar[str] = t(IndexM, "n", BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: int,
        bytes_to_read: int,
        data_to_write: List[int],
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, int, Optional[bytes], Optional[float], Optional[int]]:
        return (
            index,
            bytes_to_read,
            OptBytesM.unpack(data_to_write),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetupLiveTemperatureDisplayM:
    t: ClassVar[str] = t(IndexM, TemperatureDisplayItemM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        slot: int,
        item: Tuple[int, int, int, int, bool],
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, TemperatureDisplayItem, Optional[float], Optional[int]]:
        return (
            slot,
            TemperatureDisplayItemM.unpack(item),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SendCommandToLcdControllerM:
    t: ClassVar[str] = t(LcdRegisterM, ByteM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        location: bool, data: int, timeout: float, retry_times: int
    ) -> Tuple[LcdRegister, int, Optional[float], Optional[int]]:
        return (
            LcdRegisterM.unpack(location),
            data,
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class ConfigureKeyReportingM:
    t: ClassVar[str] = t(array(ByteM), array(ByteM), TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        when_pressed: List[int],
        when_released: List[int],
        timeout: float,
        retry_times: int,
    ) -> Tuple[Set[int], Set[int], Optional[float], Optional[int]]:
        return (
            set(when_pressed),
            set(when_released),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetSpecialCharacterDataM:
    t: ClassVar[str] = t(IndexM, SpecialCharacterM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: int,
        character: int,
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, SpecialCharacter, Optional[float], Optional[int]]:
        return (
            index,
            SpecialCharacterM.unpack(character),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetSpecialCharacterEncodingM:
    t: ClassVar[str] = "sy"


class SetAtxPowerSwitchFunctionalityM:
    t: ClassVar[str] = t(AtxPowerSwitchFunctionalitySettingsM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        settings: Tuple[List[str], bool, float], timeout: float, retry_times: int
    ) -> Tuple[AtxPowerSwitchFunctionalitySettings, Optional[float], Optional[int]]:
        return (
            AtxPowerSwitchFunctionalitySettingsM.unpack(settings),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class ConfigureWatchdogM:
    t: ClassVar[str] = t(ByteM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        timeout_seconds: int, timeout: float, retry_times: int
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (
            timeout_seconds,
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SendDataM:
    t: ClassVar[str] = t(PositionM, PositionM, BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        row: int, column: int, data: List[int], timeout: float, retry_times: int
    ) -> Tuple[int, int, bytes, Optional[float], Optional[int]]:
        return (
            row,
            column,
            BytesM.unpack(data),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetBaudRateM:
    t: ClassVar[str] = t(BaudRateM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        baud_rate: int, timeout: float, retry_times: int
    ) -> Tuple[BaudRate, Optional[float], Optional[int]]:
        return (
            BaudRateM.unpack(baud_rate),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )
