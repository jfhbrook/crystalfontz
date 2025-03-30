from typing import ClassVar, Optional, Protocol, Self, Tuple, Type, Union

from crystalfontz.config import Config
from crystalfontz.dbus.config import ConfigStruct
from crystalfontz.device import Device
from crystalfontz.response import Pong, Versions


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


class ConfigFileM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def dump(cls: Type[Self], file: Optional[str]) -> str:
        return file or cls.none


class RevisionM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def dump(cls: Type[Self], revision: Optional[str]) -> str:
        return revision or cls.none


class ConfigM:
    t: ClassVar[str] = struct(
        ConfigFileM, "ss", RevisionM.t, RevisionM.t, BaudRateM, TimeoutM, RetryTimesM
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
        payload: bytes, timeout: float, retry_times: int
    ) -> Tuple[bytes, Optional[float], Optional[int]]:
        return (payload, TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class PongM:
    t: ClassVar[str] = "y"

    @staticmethod
    def dump(pong: Pong) -> bytes:
        return pong.response


class OkM:
    t: ClassVar[str] = "b"


class TestConnectionM:
    t: ClassVar[str] = t(TimeoutM, RetryTimesM)

    @staticmethod
    def load(timeout: float, retry_times: int) -> Tuple[Optional[float], Optional[int]]:
        return (TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class GetVersionsM:
    t: ClassVar[str] = t(TimeoutM, RetryTimesM)

    @staticmethod
    def load(timeout: float, retry_times: int) -> Tuple[Optional[float], Optional[int]]:
        return (TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class VersionsM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def dump(versions: Versions) -> Tuple[str, str, str]:
        return (versions.model, versions.hardware_rev, versions.firmware_rev)


class DetectDeviceM:
    t: ClassVar[str] = t(TimeoutM, RetryTimesM)

    @staticmethod
    def load(timeout: float, retry_times: int) -> Tuple[Optional[float], Optional[int]]:
        return (TimeoutM.load(timeout), RetryTimesM.load(retry_times))


class DeviceM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def dump(device: Device) -> Tuple[str, str, str]:
        return (device.model, device.hardware_rev, device.firmware_rev)
