from typing import ClassVar, List, Tuple

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.dbus.map.base import array, t

AtxPowerSwitchFunctionT = str
AtxPowerSwitchFunctionalitySettingsT = Tuple[List[str], bool, float]


class AtxPowerSwitchFunctionM:
    t: ClassVar[str] = "s"

    @staticmethod
    def unpack(function: AtxPowerSwitchFunctionT) -> AtxPowerSwitchFunction:
        return AtxPowerSwitchFunction(function)


class AtxPowerSwitchFunctionalitySettingsM:
    t: ClassVar[str] = t(array(AtxPowerSwitchFunctionM), "bd")

    @staticmethod
    def unpack(
        settings: AtxPowerSwitchFunctionalitySettingsT,
    ) -> AtxPowerSwitchFunctionalitySettings:
        functions, auto_polarity, power_pulse_length = settings
        return AtxPowerSwitchFunctionalitySettings(
            functions={AtxPowerSwitchFunctionM.unpack(name) for name in functions},
            auto_polarity=auto_polarity,
            power_pulse_length_seconds=power_pulse_length,
        )
