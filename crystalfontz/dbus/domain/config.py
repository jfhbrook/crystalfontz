from typing import Any, cast, ClassVar, Tuple

from crystalfontz.config import Config
from crystalfontz.dbus.domain.base import (
    ModelM,
    ModelT,
    OptStrM,
    OptStrT,
    RetryTimesM,
    RetryTimesT,
    RevisionM,
    RevisionT,
    struct,
    TimeoutM,
    TimeoutT,
)
from crystalfontz.dbus.domain.baud import BaudRateM, BaudRateT

FileT = OptStrT


class FileM(OptStrM):
    t: ClassVar[str] = OptStrM.t
    none: ClassVar[str] = OptStrM.none


PortT = str


class PortM:
    t: ClassVar[str] = "s"


ConfigT = Tuple[
    FileT, PortT, ModelT, RevisionT, RevisionT, BaudRateT, TimeoutT, RetryTimesT
]


class ConfigM:
    """
    Map `Config` to and from `ConfigT`
    (`Tuple[Optional[str], str, str, str, str, int, float, int]`).
    """

    t: ClassVar[str] = struct(
        FileM,
        PortM,
        ModelM,
        RevisionM,
        RevisionM,
        BaudRateM,
        TimeoutM,
        RetryTimesM,
    )

    @staticmethod
    def pack(config: Config) -> ConfigT:
        """
        Pack `Config` to `ConfigT`.
        """

        return (
            FileM.pack(config.file),
            config.port,
            config.model,
            RevisionM.pack(config.hardware_rev),
            RevisionM.pack(config.firmware_rev),
            config.baud_rate,
            TimeoutM.pack(config.timeout),
            RetryTimesM.pack(config.retry_times),
        )

    @staticmethod
    def unpack(config: ConfigT) -> Config:
        """
        Unpack `ConfigT` to `Config`.
        """

        (
            file,
            port,
            model,
            hardware_rev,
            firmware_rev,
            baud_rate,
            timeout,
            retry_times,
        ) = config

        return cast(Any, Config)(
            file=file,
            port=port,
            model=model,
            hardware_rev=RevisionM.unpack(hardware_rev),
            firmware_rev=RevisionM.unpack(firmware_rev),
            baud_rate=baud_rate,
            timeout=TimeoutM.unpack(timeout),
            retry_times=RetryTimesM.unpack(retry_times),
        )
