from typing import ClassVar, Optional, Self, Tuple, Type

from crystalfontz.dbus.domain.base import ByteM, ByteT, Uint16M
from crystalfontz.gpio import GpioSettings, GpioState

GpioStateT = Tuple[bool, bool, bool]


class GpioStateM:
    """
    Map between GpioState and GpioStateT.
    """

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
    """
    Map between GpioSettings and GpioSettingsT.

    GPIO settings are represented by a byte, as they are in the raw
    crystalfontz protocol.
    """

    t: ClassVar[str] = ByteM.t

    @staticmethod
    def pack(settings: GpioSettings) -> GpioSettingsT:
        return settings.to_bytes()[0]

    @staticmethod
    def unpack(settings: GpioSettingsT) -> GpioSettings:
        return GpioSettings.from_byte(settings)


OptGpioSettingsT = int


class OptGpioSettingsM:
    """
    Map between Optional[GpioSettings] and OptGpioSettingsT.

    Optional GPIO settings are represented by a UINT16, where values higher
    than 0xFF are treated as None. When GPIO settings are defined, the integer
    value will be the same as with required GPIO settings.
    """

    t: ClassVar[str] = Uint16M.t
    none: ClassVar[int] = 0xFF00

    @classmethod
    def pack(cls: Type[Self], settings: Optional[GpioSettings]) -> OptGpioSettingsT:
        return GpioSettingsM.pack(settings) if settings is not None else cls.none

    @staticmethod
    def unpack(settings: OptGpioSettingsT) -> Optional[GpioSettings]:
        return GpioSettingsM.unpack(settings) if settings <= 0xFF else None
