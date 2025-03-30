from typing import ClassVar, Optional, Protocol, Tuple, Type, Union

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
    none: float = -1.0

    @staticmethod
    def load(d: float) -> Optional[float]:
        return d if d >= 0 else None


class RetryTimesM:
    t: ClassVar[str] = "i"
    none: int = -1

    @staticmethod
    def load(i: int) -> Optional[int]:
        return i if i >= 0 else None


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
