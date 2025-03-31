from typing import (
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    Self,
    Set,
    Tuple,
    Type,
    Union,
)

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.character import SpecialCharacter
from crystalfontz.config import Config
from crystalfontz.cursor import CursorStyle
from crystalfontz.dbus.config import ConfigStruct
from crystalfontz.device import Device
from crystalfontz.lcd import LcdRegister
from crystalfontz.response import (
    DowDeviceInformation,
    DowTransactionResult,
    KeypadPolled,
    LcdMemory,
    Pong,
    UserFlashAreaRead,
    Versions,
)
from crystalfontz.temperature import TemperatureDisplayItem, TemperatureUnit


class TypeProtocol(Protocol):
    t: ClassVar[str]


def t(*args: Union[str, Type[TypeProtocol]]) -> str:
    type_ = ""

    for arg in args:
        if isinstance(arg, str):
            type_ += arg
        else:
            type_ += arg.t

    return type_


def struct(*args: Union[str, Type[TypeProtocol]]) -> str:
    return t("(", *args, ")")


def array(of: Union[str, Type[TypeProtocol]]) -> str:
    return f"a{t(of)}"


class OptIntM:
    t: ClassVar[str] = "i"
    none: ClassVar[int] = -1

    @staticmethod
    def unpack(r: int) -> Optional[int]:
        return r if r >= 0 else None

    @classmethod
    def pack(cls: Type[Self], r: Optional[int]) -> int:
        return r if r is not None else cls.none


class OptFloatM:
    t: ClassVar[str] = "d"
    none: ClassVar[float] = -1.0

    @staticmethod
    def unpack(t: float) -> Optional[float]:
        return t if t >= 0 else None

    @classmethod
    def pack(cls: Type[Self], t: Optional[float]) -> float:
        return t if t is not None else cls.none


class AddressM:
    t: ClassVar[str] = "q"


class IndexM:
    t: ClassVar[str] = "q"


class PositionM:
    t: ClassVar[str] = "q"


class ByteM:
    t: ClassVar[str] = "y"


class BytesM:
    t: ClassVar[str] = array(ByteM)

    @staticmethod
    def unpack(buff: List[int]) -> bytes:
        return bytes(buff)

    # TODO: This may not be what the dbus client expects...
    @staticmethod
    def pack(buff: bytes) -> List[int]:
        return list(buff)


class OptBytesM:
    t: ClassVar[str] = array(ByteM)
    none: ClassVar[List[int]] = list()

    @staticmethod
    def unpack(buff: List[int]) -> Optional[bytes]:
        if not buff:
            return None
        return BytesM.unpack(buff)

    @classmethod
    def pack(cls: Type[Self], buff: Optional[bytes]) -> List[int]:
        if buff is None:
            return cls.none
        return BytesM.pack(buff)


class ConfigFileM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def pack(cls: Type[Self], file: Optional[str]) -> str:
        return file or cls.none


class PortM:
    t: ClassVar[str] = "s"


class ModelM:
    t: ClassVar[str] = "s"


class RevisionM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def pack(cls: Type[Self], revision: Optional[str]) -> str:
        return revision or cls.none


class BaudRateM:
    t: ClassVar[str] = "q"


class TimeoutM(OptFloatM):
    pass


class RetryTimesM(OptIntM):
    pass


class ConfigM:
    t: ClassVar[str] = struct(
        ConfigFileM,
        PortM,
        ModelM,
        RevisionM,
        RevisionM,
        BaudRateM,
        TimeoutM,
        RetryTimesM,
    )

    @staticmethod
    def pack(config: Config) -> ConfigStruct:
        return (
            ConfigFileM.pack(config.file),
            config.port,
            config.model,
            RevisionM.pack(config.hardware_rev),
            RevisionM.pack(config.firmware_rev),
            config.baud_rate,
            TimeoutM.pack(config.timeout),
            RetryTimesM.pack(config.retry_times),
        )


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


class PongM:
    t: ClassVar[str] = BytesM.t

    @staticmethod
    def pack(pong: Pong) -> List[int]:
        return BytesM.pack(pong.response)


class OkM:
    t: ClassVar[str] = "b"


class SimpleCommandM:
    t: ClassVar[str] = t(TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        timeout: float, retry_times: int
    ) -> Tuple[Optional[float], Optional[int]]:
        return (TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class VersionsM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def unpack(versions: Tuple[str, str, str]) -> Versions:
        return Versions(*versions)

    @staticmethod
    def pack(versions: Versions) -> Tuple[str, str, str]:
        return (versions.model, versions.hardware_rev, versions.firmware_rev)


class DeviceM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def pack(device: Device) -> Tuple[str, str, str]:
        return (device.model, device.hardware_rev, device.firmware_rev)


class WriteUserFlashAreaM:
    t: ClassVar[str] = t("y", TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        data: bytes, timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (data, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


class UserFlashAreaReadM:
    t: ClassVar[str] = "y"

    @staticmethod
    def pack(res: UserFlashAreaRead) -> bytes:
        return res.data


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


class LcdMemoryM:
    t: ClassVar[str] = t("q", BytesM)

    @staticmethod
    def unpack(obj: Tuple[int, List[int]]) -> LcdMemory:
        address, buff = obj
        return LcdMemory(address, BytesM.unpack(buff))

    @staticmethod
    def pack(memory: LcdMemory) -> Tuple[int, List[int]]:
        return (memory.address, BytesM.pack(memory.data))


class SetCursorPositionM:
    t: ClassVar[str] = t(PositionM, PositionM, TimeoutM, RetryTimesM)

    @staticmethod
    def unpack(
        row: int, column: int, timeout: float, retry_times: int
    ) -> Tuple[int, int, Optional[float], Optional[int]]:
        return (row, column, TimeoutM.unpack(timeout), RetryTimesM.unpack(retry_times))


CURSOR_STYLES: Dict[int, CursorStyle] = {style.value: style for style in CursorStyle}


class CursorStyleM:
    t: ClassVar[str] = "q"

    @staticmethod
    def unpack(style: int) -> CursorStyle:
        return CURSOR_STYLES[style]

    @staticmethod
    def pack(style: CursorStyle) -> int:
        return style.value


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


class DowDeviceInformationM:
    t: ClassVar[str] = t(IndexM, BytesM)

    @staticmethod
    def unpack(info: Tuple[int, List[int]]) -> DowDeviceInformation:
        index, rom_id = info
        return DowDeviceInformation(index, BytesM.unpack(rom_id))

    @staticmethod
    def pack(info: DowDeviceInformation) -> Tuple[int, List[int]]:
        return (info.index, BytesM.pack(info.rom_id))


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


class DowTransactionResultM:
    t: ClassVar[str] = t(IndexM, BytesM, "q")

    @staticmethod
    def unpack(res: Tuple[int, List[int], int]) -> DowTransactionResult:
        index, data, crc = res
        return DowTransactionResult(index, BytesM.unpack(data), crc)

    @staticmethod
    def pack(res: DowTransactionResult) -> Tuple[int, List[int], int]:
        return (res.index, BytesM.pack(res.data), res.crc)


class TemperatureDigitsM:
    t: ClassVar[str] = "n"

    @staticmethod
    def unpack(n_digits: int) -> Literal[3] | Literal[5]:
        if n_digits != 3 or n_digits != 5:
            raise ValueError("May display either 3 or 5 temperature digits")
        return n_digits


TEMPERATURE_UNITS: Dict[bool, TemperatureUnit] = {
    bool(unit.value): unit for unit in TemperatureUnit
}


class TemperatureUnitM:
    t: ClassVar[str] = "b"

    @staticmethod
    def unpack(unit: bool) -> TemperatureUnit:
        return TEMPERATURE_UNITS[unit]

    @staticmethod
    def pack(unit: TemperatureUnit) -> bool:
        return bool(unit.value)


class TemperatureDisplayItemM:
    t: ClassVar[str] = t(IndexM, TemperatureDigitsM, PositionM, PositionM, "b")

    @staticmethod
    def unpack(
        item: Tuple[int, int, int, int, bool],
    ) -> TemperatureDisplayItem:

        index, n_digits, column, row, units = item
        return TemperatureDisplayItem(
            index,
            TemperatureDigitsM.unpack(n_digits),
            column,
            row,
            TemperatureUnitM.unpack(units),
        )

    @staticmethod
    def pack(item: TemperatureDisplayItem) -> Tuple[int, int, int, int, bool]:
        return (
            item.index,
            item.n_digits,
            item.column,
            item.row,
            TemperatureUnitM.pack(item.units),
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


LCD_REGISTERS: Dict[bool, LcdRegister] = {
    bool(register.value): register for register in LcdRegister
}


class LcdRegisterM:
    t: ClassVar[str] = "b"

    @staticmethod
    def unpack(register: bool) -> LcdRegister:
        return LCD_REGISTERS[register]

    @staticmethod
    def pack(register: LcdRegister) -> bool:
        return bool(register.value)


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


class SpecialCharacterM:
    t: ClassVar[str] = "t"

    @staticmethod
    def unpack(character: int) -> SpecialCharacter:
        raise NotImplementedError("load")


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


class KeypadPolledM:
    t: ClassVar[str] = array(struct("bbb"))

    @staticmethod
    def pack(polled: KeypadPolled) -> List[Tuple[bool, bool, bool]]:
        raise NotImplementedError("pack")

    @staticmethod
    def unpack(polled: List[Tuple[bool, bool, bool]]) -> KeypadPolled:
        raise NotImplementedError("unpack")


class AtxPowerSwitchFunctionalitySettingsM:
    t: ClassVar[str] = t(array("s"), "bd")

    @staticmethod
    def unpack(
        settings: Tuple[List[str], bool, float],
    ) -> AtxPowerSwitchFunctionalitySettings:
        functions, auto_polarity, power_pulse_length = settings
        return AtxPowerSwitchFunctionalitySettings(
            functions={AtxPowerSwitchFunction[name] for name in functions},
            auto_polarity=auto_polarity,
            power_pulse_length_seconds=power_pulse_length,
        )


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


class StatusM:
    t: ClassVar[str] = ""


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
