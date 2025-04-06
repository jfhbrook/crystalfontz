from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Optional, Self, Set, Type

AUTO_POLARITY = 0x01
RESET_INVERT = 0x02
POWER_INVERT = 0x04


class AtxPowerSwitchFunction(Enum):
    """
    An ATX power switch function.

    Refer to your device's datasheet for the effects of each of these functions.
    """

    LCD_OFF_IF_HOST_IS_OFF = 0x10
    KEYPAD_RESET = 0x20
    KEYPAD_POWER_ON = 0x40
    KEYPAD_POWER_OFF = 0x80


@dataclass
class AtxPowerSwitchFunctionalitySettings:
    functions: Set[AtxPowerSwitchFunction]
    auto_polarity: bool = True
    reset_invert: bool = False
    power_invert: bool = False
    power_pulse_length_seconds: Optional[float] = None

    """
    Settings for command 28 (0x1C): Set ATX Power Switch Functionality.

    Parameters:
        functions (Set[AtxPowerSwitchFunction): A set of enabled power switch functions.
        auto_polarity (bool): When True, automatically detects polarity for reset and/or
                              power (recommended)
        reset_invert (bool): When True, the reset pin drives high instead of low
        power_invert (bool): When True, the power pin drives high instead of low
        power_pulse_length_seconds (Optional[float]): Length of power on and off
                                                      pulses in seconds. When set to 8
                                                      seconds or higher, asserts power
                                                      control line until host power
                                                      state changes.

    """

    @classmethod
    def from_bytes(cls: Type[Self], settings: bytes) -> Self:
        functions: Set[AtxPowerSwitchFunction] = set()
        for function in AtxPowerSwitchFunction:
            if settings[0] & function.value:
                functions.add(function)
        auto_polarity: bool = bool(settings[0] & AUTO_POLARITY)
        reset_invert: bool = bool(settings[0] & RESET_INVERT)
        power_invert: bool = bool(settings[0] & POWER_INVERT)
        power_pulse_length_seconds: Optional[float] = (
            settings[1] / 32 if len(settings) > 1 else None
        )

        return cls(
            functions=functions,
            auto_polarity=auto_polarity,
            reset_invert=reset_invert,
            power_invert=power_invert,
            power_pulse_length_seconds=power_pulse_length_seconds,
        )

    def to_bytes(self: Self) -> bytes:
        functions: int = 0
        for function in self.functions:
            functions ^= function.value
        if self.auto_polarity:
            functions ^= AUTO_POLARITY
        if self.reset_invert:
            functions ^= RESET_INVERT
        if self.power_invert:
            functions ^= POWER_INVERT

        packed: bytes = functions.to_bytes(1, "big")

        if self.power_pulse_length_seconds is not None:
            pulse_length = int(self.power_pulse_length_seconds * 32)

            if pulse_length < 1:
                raise ValueError(f"Pulse length can not be less than {1/32}")

            packed += min(pulse_length, 255).to_bytes(1, "big")

        return packed

    def as_dict(self: Self) -> Dict[str, Any]:
        as_ = asdict(self)

        as_["functions"] = [fn.value for fn in self.functions]

        return as_

    def __repr__(self: Self) -> str:
        repr_ = f"Functions enabled: {', '.join([e.name for e in self.functions])}\n"
        repr_ += f"Auto-Polarity Enabled: {'yes' if self.auto_polarity else 'no'}\n"
        repr_ += f"Reset Inverted: {'yes' if self.reset_invert else 'no'}\n"
        repr_ += f"Power Inverted: {'yes' if self.power_invert else 'no'}\n"
        repr_ += f"Power Pulse Length (seconds): {self.power_pulse_length_seconds}"
        return repr_
