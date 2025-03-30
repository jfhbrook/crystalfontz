from typing import ClassVar, List, Optional, Protocol, Self, Tuple, Type, Union

from crystalfontz.config import Config
from crystalfontz.dbus.config import ConfigStruct
from crystalfontz.device import Device
from crystalfontz.response import LcdMemory, Pong, UserFlashAreaRead, Versions


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


class BytesM:
    t: ClassVar[str] = array("y")

    @staticmethod
    def load(buff: List[int]) -> bytes:
        return bytes(buff)

    # TODO: This may not be what the dbus client expects...
    @staticmethod
    def dump(buff: bytes) -> List[int]:
        return list(buff)


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


class TimeoutM:
    t: ClassVar[str] = "d"
    none: ClassVar[float] = -1.0

    @staticmethod
    def load(t: float) -> Optional[float]:
        return t if t >= 0 else None

    @classmethod
    def dump(cls: Type[Self], t: Optional[float]) -> float:
        return t if t is not None else cls.none


class RetryTimesM:
    t: ClassVar[str] = "i"
    none: ClassVar[int] = -1

    @staticmethod
    def load(r: int) -> Optional[int]:
        return r if r >= 0 else None

    @classmethod
    def dump(cls: Type[Self], r: Optional[int]) -> int:
        return r if r is not None else cls.none


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
    t: ClassVar[str] = t("y", TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        line: bytes, timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (line, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class ReadLcdMemoryM:
    t: ClassVar[str] = t("n", TimeoutM, RetryTimesM)

    @staticmethod
    def load(
        address: int, timeout: float, retry_times: int
    ) -> Tuple[int, Optional[float], Optional[int]]:
        return (address, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class LcdMemoryM:
    t: ClassVar[str] = t("n", BytesM)

    @staticmethod
    def load(obj: Tuple[int, List[int]]) -> LcdMemory:
        address, buff = obj
        return LcdMemory(address, BytesM.load(buff))

    @staticmethod
    def dump(memory: LcdMemory) -> Tuple[int, List[int]]:
        return (memory.address, BytesM.dump(memory.data))
