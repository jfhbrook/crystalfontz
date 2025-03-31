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

from crystalfontz.character import SpecialCharacter
from crystalfontz.config import Config
from crystalfontz.cursor import CursorStyle
from crystalfontz.dbus.config import ConfigStruct
from crystalfontz.device import Device
from crystalfontz.lcd import LcdRegister
from crystalfontz.response import (
    DowDeviceInformation,
    DowTransactionResult,
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
    def load(r: int) -> Optional[int]:
        return r if r >= 0 else None

    @classmethod
    def dump(cls: Type[Self], r: Optional[int]) -> int:
        return r if r is not None else cls.none


class OptFloatM:
    t: ClassVar[str] = "d"
    none: ClassVar[float] = -1.0

    @staticmethod
    def load(t: float) -> Optional[float]:
        return t if t >= 0 else None

    @classmethod
    def dump(cls: Type[Self], t: Optional[float]) -> float:
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
    def load(buff: List[int]) -> bytes:
        return bytes(buff)

    # TODO: This may not be what the dbus client expects...
    @staticmethod
    def dump(buff: bytes) -> List[int]:
        return list(buff)


class OptBytesM:
    t: ClassVar[str] = array(ByteM)
    none: ClassVar[List[int]] = list()

    @staticmethod
    def load(buff: List[int]) -> Optional[bytes]:
        if not buff:
            return None
        return BytesM.load(buff)

    @classmethod
    def dump(cls: Type[Self], buff: Optional[bytes]) -> List[int]:
        if buff is None:
            return cls.none
        return BytesM.dump(buff)


class ConfigFileM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def dump(cls: Type[Self], file: Optional[str]) -> str:
        return file or cls.none


class PortM:
    t: ClassVar[str] = "s"


class ModelM:
    t: ClassVar[str] = "s"


class RevisionM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def dump(cls: Type[Self], revision: Optional[str]) -> str:
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
    def dump(config: Config) -> ConfigStruct:
        return (
            ConfigFileM.dump(config.file),
            config.port,
            config.model,
            RevisionM.dump(config.hardware_rev),
            RevisionM.dump(config.firmware_rev),
            config.baud_rate,
            TimeoutM.dump(config.timeout),
            RetryTimesM.dump(config.retry_times),
        )


class PingM:
    t: ClassVar[str] = t("y", TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        payload: List[int], timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (
            BytesM.load(payload),
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


class PongM:
    t: ClassVar[str] = BytesM.t

    @staticmethod
    def dump(pong: Pong) -> List[int]:
        return BytesM.dump(pong.response)


class OkM:
    t: ClassVar[str] = "b"


class SimpleCommandM:
    t: ClassVar[str] = t(TimeoutM, RetryTimesM)

    @staticmethod
    def load(timeout: float, retry_times: int) -> Tuple[Optional[float], Optional[int]]:
        return (TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class VersionsM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def load(versions: Tuple[str, str, str]) -> Versions:
        return Versions(*versions)

    @staticmethod
    def dump(versions: Versions) -> Tuple[str, str, str]:
        return (versions.model, versions.hardware_rev, versions.firmware_rev)


class DeviceM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def dump(device: Device) -> Tuple[str, str, str]:
        return (device.model, device.hardware_rev, device.firmware_rev)


class WriteUserFlashAreaM:
    t: ClassVar[str] = t("y", TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        data: bytes, timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (data, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class UserFlashAreaReadM:
    t: ClassVar[str] = "y"

    @staticmethod
    def dump(res: UserFlashAreaRead) -> bytes:
        return res.data


class SetLineM:
    t: ClassVar[str] = t(BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        line: bytes, timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (line, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class ReadLcdMemoryM:
    t: ClassVar[str] = t(AddressM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        address: int, timeout: float, retry_times: int
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (address, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class LcdMemoryM:
    t: ClassVar[str] = t("q", BytesM)

    @staticmethod
    def load(obj: Tuple[int, List[int]]) -> LcdMemory:
        address, buff = obj
        return LcdMemory(address, BytesM.load(buff))

    @staticmethod
    def dump(memory: LcdMemory) -> Tuple[int, List[int]]:
        return (memory.address, BytesM.dump(memory.data))


class SetCursorPositionM:
    t: ClassVar[str] = t(PositionM, PositionM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        row: int, column: int, timeout: float, retry_times: int
    ) -> Tuple[int, int, Optional[float], Optional[int]]:
        return (row, column, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


CURSOR_STYLES: Dict[int, CursorStyle] = {style.value: style for style in CursorStyle}


class CursorStyleM:
    t: ClassVar[str] = "q"

    @staticmethod
    def load(style: int) -> CursorStyle:
        return CURSOR_STYLES[style]

    @staticmethod
    def dump(style: CursorStyle) -> int:
        return style.value


class SetCursorStyleM:
    t: ClassVar[str] = t(CursorStyleM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        style: int, timeout: float, retry_times: int
    ) -> Tuple[CursorStyle, Optional[float], Optional[int]]:
        return (
            CursorStyleM.load(style),
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


class SetContrastM:
    t: ClassVar[str] = t("d", TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        contrast: float, timeout: float, retry_times: int
    ) -> Tuple[float, Optional[float], Optional[int]]:
        return (contrast, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class SetBacklightM:
    t: ClassVar[str] = t("dd", TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        lcd_brightness: float,
        keypad_brightness: float,
        timeout: float,
        retry_times: int,
    ) -> Tuple[float, Optional[float], Optional[float], Optional[int]]:
        return (
            lcd_brightness,
            OptFloatM.load(keypad_brightness),
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


class ReadDowDeviceInformationM:
    t: ClassVar[str] = t(IndexM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        index: int, timeout: float, retry_times: int
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (index, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class DowDeviceInformationM:
    t: ClassVar[str] = t(IndexM, BytesM)

    @staticmethod
    def load(info: Tuple[int, List[int]]) -> DowDeviceInformation:
        index, rom_id = info
        return DowDeviceInformation(index, BytesM.load(rom_id))

    @staticmethod
    def dump(info: DowDeviceInformation) -> Tuple[int, List[int]]:
        return (info.index, BytesM.dump(info.rom_id))


class SetupTemperatureReportingM:
    t: ClassVar[str] = t(array("q"), TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        enabled: List[int], timeout: float, retry_times: int
    ) -> Tuple[List[int], Optional[float], Optional[int]]:
        return (enabled, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class DowTransactionM:
    t: ClassVar[str] = t(IndexM, "n", BytesM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        index: int,
        bytes_to_read: int,
        data_to_write: List[int],
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, int, Optional[bytes], Optional[float], Optional[int]]:
        return (
            index,
            bytes_to_read,
            OptBytesM.load(data_to_write),
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


class DowTransactionResultM:
    t: ClassVar[str] = t(IndexM, BytesM, "q")

    @staticmethod
    def load(res: Tuple[int, List[int], int]) -> DowTransactionResult:
        index, data, crc = res
        return DowTransactionResult(index, BytesM.load(data), crc)

    @staticmethod
    def dump(res: DowTransactionResult) -> Tuple[int, List[int], int]:
        return (res.index, BytesM.dump(res.data), res.crc)


class TemperatureDigitsM:
    t: ClassVar[str] = "n"

    @staticmethod
    def load(n_digits: int) -> Literal[3] | Literal[5]:
        if n_digits != 3 or n_digits != 5:
            raise ValueError("May display either 3 or 5 temperature digits")
        return n_digits


TEMPERATURE_UNITS: Dict[bool, TemperatureUnit] = {
    bool(unit.value): unit for unit in TemperatureUnit
}


class TemperatureUnitM:
    t: ClassVar[str] = "b"

    @staticmethod
    def load(unit: bool) -> TemperatureUnit:
        return TEMPERATURE_UNITS[unit]

    @staticmethod
    def dump(unit: TemperatureUnit) -> bool:
        return bool(unit.value)


class TemperatureDisplayItemM:
    t: ClassVar[str] = t(IndexM, TemperatureDigitsM, PositionM, PositionM, "b")

    @staticmethod
    def load(
        item: Tuple[int, int, int, int, bool],
    ) -> TemperatureDisplayItem:

        index, n_digits, column, row, units = item
        return TemperatureDisplayItem(
            index,
            TemperatureDigitsM.load(n_digits),
            column,
            row,
            TemperatureUnitM.load(units),
        )

    @staticmethod
    def dump(item: TemperatureDisplayItem) -> Tuple[int, int, int, int, bool]:
        return (
            item.index,
            item.n_digits,
            item.column,
            item.row,
            TemperatureUnitM.dump(item.units),
        )


class SetupLiveTemperatureDisplayM:
    t: ClassVar[str] = t(IndexM, TemperatureDisplayItemM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        slot: int,
        item: Tuple[int, int, int, int, bool],
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, TemperatureDisplayItem, Optional[float], Optional[int]]:
        return (
            slot,
            TemperatureDisplayItemM.load(item),
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


LCD_REGISTERS: Dict[bool, LcdRegister] = {
    bool(register.value): register for register in LcdRegister
}


class LcdRegisterM:
    t: ClassVar[str] = "b"

    @staticmethod
    def load(register: bool) -> LcdRegister:
        return LCD_REGISTERS[register]

    @staticmethod
    def dump(register: LcdRegister) -> bool:
        return bool(register.value)


class SendCommandToLcdControllerM:
    t: ClassVar[str] = t(LcdRegisterM, ByteM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        location: bool, data: int, timeout: float, retry_times: int
    ) -> Tuple[LcdRegister, int, Optional[float], Optional[int]]:
        return (
            LcdRegisterM.load(location),
            data,
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


class ConfigureKeyReportingM:
    t: ClassVar[str] = t(array(ByteM), array(ByteM), TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        when_pressed: List[int],
        when_released: List[int],
        timeout: float,
        retry_times: int,
    ) -> Tuple[Set[int], Set[int], Optional[float], Optional[int]]:
        return (
            set(when_pressed),
            set(when_released),
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


class SpecialCharacterM:
    t: ClassVar[str] = "t"

    @staticmethod
    def load(character: int) -> SpecialCharacter:
        raise NotImplementedError("load")


class SetSpecialCharacterDataM:
    t: ClassVar[str] = t(IndexM, SpecialCharacterM, TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        index: int,
        character: int,
        timeout: float,
        retry_times: int,
    ) -> Tuple[int, SpecialCharacter, Optional[float], Optional[int]]:
        return (
            index,
            SpecialCharacterM.load(character),
            TimeoutM.load(timeout),
            RetryTimesM.load(retry_times),
        )


class SetSpecialCharacterEncodingM:
    t: ClassVar[str] = "sy"
