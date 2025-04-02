from typing import ClassVar, Dict, List, Tuple

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.dbus.domain.base import array, ByteM, ByteT, OptFloatM, OptFloatT, t

AtxPowerSwitchFunctionT = ByteT

AutoPolarityT = bool
ResetInvertT = bool
PowerInvertT = bool
PulseLengthT = OptFloatT
AtxPowerSwitchFunctionalitySettingsT = Tuple[
    List[AtxPowerSwitchFunctionT],
    AutoPolarityT,
    ResetInvertT,
    PowerInvertT,
    PulseLengthT,
]


FUNCTIONS: Dict[ByteT, AtxPowerSwitchFunction] = {
    function.value: function for function in AtxPowerSwitchFunction
}


class AtxPowerSwitchFunctionM:
    t: ClassVar[str] = ByteM.t

    @staticmethod
    def unpack(function: AtxPowerSwitchFunctionT) -> AtxPowerSwitchFunction:
        try:
            return FUNCTIONS[function]
        except KeyError:
            raise ValueError(f"{function} is not a valid ATX power switch function")


class AtxPowerSwitchFunctionalitySettingsM:
    t: ClassVar[str] = t(array(AtxPowerSwitchFunctionM), "bbb", OptFloatM)

    @staticmethod
    def unpack(
        settings: AtxPowerSwitchFunctionalitySettingsT,
    ) -> AtxPowerSwitchFunctionalitySettings:
        functions, auto_polarity, reset_invert, power_invert, power_pulse_length = (
            settings
        )
        return AtxPowerSwitchFunctionalitySettings(
            functions={AtxPowerSwitchFunctionM.unpack(name) for name in functions},
            auto_polarity=auto_polarity,
            reset_invert=reset_invert,
            power_invert=power_invert,
            power_pulse_length_seconds=OptFloatM.unpack(power_pulse_length),
        )
