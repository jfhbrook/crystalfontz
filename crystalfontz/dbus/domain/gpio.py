from typing import ClassVar, Dict, Optional, Self, Tuple, Type

from crystalfontz.dbus.domain.base import ByteM, ByteT
from crystalfontz.gpio import GpioDriveMode, GpioFunction, GpioSettings, GpioState

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


GpioFunctionT = ByteT

GPIO_FUNCTIONS: Dict[ByteT, GpioFunction] = {
    function.value: function for function in GpioFunction
}


class GpioFunctionM:
    """
    Map GpioFunction to and from dbus types.
    """

    t: ClassVar[str] = ByteM.t

    @staticmethod
    def pack(function: GpioFunction) -> GpioFunctionT:
        return function.value

    @staticmethod
    def unpack(function: GpioFunctionT) -> GpioFunction:
        return GPIO_FUNCTIONS[function]


GpioDriveModeT = ByteT

GPIO_DRIVE_MODES: Dict[ByteT, GpioDriveMode] = {
    drive_mode.value: drive_mode for drive_mode in GpioDriveMode
}


class GpioDriveModeM:
    """
    Map GpioDriveMode to and from dbus types.
    """

    t: ClassVar[str] = ByteM.t

    @staticmethod
    def pack(drive_mode: GpioDriveMode) -> GpioDriveModeT:
        return drive_mode.value

    @staticmethod
    def unpack(drive_mode: GpioDriveModeT) -> GpioDriveMode:
        return GPIO_DRIVE_MODES[drive_mode]


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
