from typing import ClassVar, List, Tuple

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.dbus.map.base import array, t


class AtxPowerSwitchFunctionalitySettingsM:
    t: ClassVar[str] = t(array("s"), "bd")

    @staticmethod
    def unpack(
        settings: Tuple[List[str], bool, float],
    ) -> AtxPowerSwitchFunctionalitySettings:
        functions, auto_polarity, power_pulse_length = settings
        return AtxPowerSwitchFunctionalitySettings(
            functions={AtxPowerSwitchFunction[name] for name in functions},
            auto_polarity=auto_polarity,
            power_pulse_length_seconds=power_pulse_length,
        )
