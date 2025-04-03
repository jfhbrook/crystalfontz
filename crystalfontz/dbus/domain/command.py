from typing import ClassVar, List, Optional, Set, Tuple

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate
from crystalfontz.character import SpecialCharacter
from crystalfontz.cursor import CursorStyle
from crystalfontz.dbus.domain.atx import (
    AtxPowerSwitchFunctionalitySettingsM,
    AtxPowerSwitchFunctionalitySettingsT,
)
from crystalfontz.dbus.domain.base import (
    AddressM,
    AddressT,
    array,
    ByteM,
    BytesM,
    ByteT,
    IndexM,
    IndexT,
    OptBytesM,
    OptBytesT,
    PositionM,
    PositionT,
    RetryTimesM,
    RetryTimesT,
    struct,
    t,
    TimeoutM,
    TimeoutT,
    Uint16M,
    Uint16T,
)
from crystalfontz.dbus.domain.baud import BaudRateM, BaudRateT
from crystalfontz.dbus.domain.character import SpecialCharacterM, SpecialCharacterT
from crystalfontz.dbus.domain.cursor import CursorStyleM, CursorStyleT
from crystalfontz.dbus.domain.gpio import OptGpioSettingsM, OptGpioSettingsT
from crystalfontz.dbus.domain.keys import (
    KeypadBrightnessM,
    KeypadBrightnessT,
    KeyPressM,
    KeyPressT,
)
from crystalfontz.dbus.domain.lcd import LcdRegisterM, LcdRegisterT
from crystalfontz.dbus.domain.temperature import (
    TemperatureDisplayItemM,
    TemperatureDisplayItemT,
)
from crystalfontz.gpio import GpioSettings
from crystalfontz.keys import KeyPress
from crystalfontz.lcd import LcdRegister
from crystalfontz.temperature import TemperatureDisplayItem


class SimpleCommandM:
    t: ClassVar[str] = t(TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[Optional[float], Optional[int]]:
        return (TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class PingM:
    t: ClassVar[str] = t(BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        payload: bytes, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (
            payload,
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class WriteUserFlashAreaM:
    t: ClassVar[str] = t(BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        data: bytes, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (
            data,
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetLineM:
    t: ClassVar[str] = t(BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        line: bytes, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (
            line,
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class ReadLcdMemoryM:
    t: ClassVar[str] = t(AddressM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        address: AddressT, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (address, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetCursorPositionM:
    t: ClassVar[str] = t(PositionM, PositionM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        row: int, column: int, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[int, int, Optional[float], Optional[int]]:
        return (row, column, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetCursorStyleM:
    t: ClassVar[str] = t(CursorStyleM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        style: CursorStyleT, timeout: TimeoutT, retry_times: RetryTimesT
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
        contrast: float, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[float, Optional[float], Optional[int]]:
        return (contrast, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetBacklightM:
    t: ClassVar[str] = t("d", KeypadBrightnessM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        lcd_brightness: float,
        keypad_brightness: KeypadBrightnessT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> Tuple[float, Optional[float], Optional[float], Optional[int]]:
        return (
            lcd_brightness,
            KeypadBrightnessM.unpack(keypad_brightness),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class ReadDowDeviceInformationM:
    t: ClassVar[str] = t(IndexM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: IndexT, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (index, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class SetupTemperatureReportingM:
    t: ClassVar[str] = t(array(IndexM), TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        enabled: List[IndexT], timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[List[int], Optional[float], Optional[int]]:
        return (enabled, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class DowTransactionM:
    t: ClassVar[str] = t(IndexM, Uint16M, BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: IndexT,
        bytes_to_read: Uint16T,
        data_to_write: OptBytesT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
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
        slot: IndexT,
        item: TemperatureDisplayItemT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
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
        location: LcdRegisterT, data: ByteT, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[LcdRegister, int, Optional[float], Optional[int]]:
        return (
            LcdRegisterM.unpack(location),
            data,
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class ConfigureKeyReportingM:
    t: ClassVar[str] = t(array(KeyPressM), array(ByteM), TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        when_pressed: List[KeyPressT],
        when_released: List[KeyPressT],
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> Tuple[Set[KeyPress], Set[KeyPress], Optional[float], Optional[int]]:
        return (
            {KeyPressM.unpack(keypress) for keypress in when_pressed},
            {KeyPressM.unpack(keypress) for keypress in when_released},
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetSpecialCharacterDataM:
    t: ClassVar[str] = t(IndexM, SpecialCharacterM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: IndexT,
        character: SpecialCharacterT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
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
    t: ClassVar[str] = t(
        struct(AtxPowerSwitchFunctionalitySettingsM), TimeoutM, RetryTimesM
    )

    @staticmethod
    def unpack(
        settings: AtxPowerSwitchFunctionalitySettingsT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
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
        timeout_seconds: ByteT, timeout: TimeoutT, retry_times: RetryTimesT
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
        row: PositionT,
        column: PositionT,
        data: bytes,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> Tuple[int, int, bytes, Optional[float], Optional[int]]:
        return (
            row,
            column,
            data,
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetBaudRateM:
    t: ClassVar[str] = t(BaudRateM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        baud_rate: BaudRateT, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[BaudRate, Optional[float], Optional[int]]:
        return (
            BaudRateM.unpack(baud_rate),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class SetGpioM:
    t: ClassVar[str] = t(IndexM, ByteM, OptGpioSettingsM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: IndexT,
        output_state: ByteT,
        settings: OptGpioSettingsT,
        timeout: TimeoutT,
        retry_times: RetryTimesT,
    ) -> Tuple[int, int, Optional[GpioSettings], Optional[float], Optional[int]]:
        return (
            index,
            output_state,
            OptGpioSettingsM.unpack(settings),
            TimeoutM.unpack(timeout),
            RetryTimesM.unpack(retry_times),
        )


class ReadGpioM:
    t: ClassVar[str] = t(IndexM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        index: IndexT, timeout: TimeoutT, retry_times: RetryTimesT
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (index, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))
