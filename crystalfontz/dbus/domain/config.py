from typing import Any, cast, ClassVar, Optional, Self, Tuple, Type

from crystalfontz.config import Config
from crystalfontz.dbus.domain.base import (
    ModelM,
    ModelT,
    RetryTimesM,
    RetryTimesT,
    RevisionM,
    RevisionT,
    struct,
    TimeoutM,
    TimeoutT,
)
from crystalfontz.dbus.domain.baud import BaudRateM, BaudRateT

FileT = str


class FileM:
    t: ClassVar[str] = "s"
    none: ClassVar[str] = ""

    @classmethod
    def pack(cls: Type[Self], file: Optional[str]) -> str:
        return file or cls.none


PortT = str


class PortM:
    t: ClassVar[str] = "s"


ConfigT = Tuple[
    FileT, PortT, ModelT, RevisionT, RevisionT, BaudRateT, TimeoutT, RetryTimesT
]


class ConfigM:
    """
    Map a config to and from dbus types.
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
