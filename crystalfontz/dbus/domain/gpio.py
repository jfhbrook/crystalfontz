from typing import ClassVar, Optional, Self, Tuple, Type

from crystalfontz.dbus.domain.base import ByteM, ByteT
from crystalfontz.gpio import GpioSettings, GpioState

GpioStateT = Tuple[bool, bool, bool]


class GpioStateM:
    t: ClassVar[str] = "bbb"

    @staticmethod
    def pack(state: GpioState) -> GpioStateT:
        return (state.state, state.falling, state.rising)

    @staticmethod
    def unpack(state: GpioStateT) -> GpioState:
        st, falling, rising = state
        return GpioState(st, falling, rising)


GpioSettingsT = ByteT


class GpioSettingsM:
    t: ClassVar[str] = ByteM.t

    @staticmethod
    def pack(settings: GpioSettings) -> GpioSettingsT:
        return settings.to_bytes()[0]

    @staticmethod
    def unpack(settings: GpioSettingsT) -> GpioSettings:
        return GpioSettings.from_byte(settings)


OptGpioSettingsT = int


class OptGpioSettingsM:
    t: ClassVar[str] = "n"
    none: ClassVar[int] = -1

    @classmethod
    def pack(cls: Type[Self], settings: Optional[GpioSettings]) -> OptGpioSettingsT:
        return GpioSettingsM.pack(settings) if settings is not None else cls.none

    @staticmethod
    def unpack(settings: OptGpioSettingsT) -> Optional[GpioSettings]:
        return GpioSettingsM.unpack(settings) if settings >= 0 else None
