from typing import ClassVar, Optional, Self, Type

from crystalfontz.config import Config
from crystalfontz.dbus.config import ConfigStruct
from crystalfontz.dbus.map.base import RetryTimesM, struct, TimeoutM
from crystalfontz.dbus.map.baud import BaudRateM


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
