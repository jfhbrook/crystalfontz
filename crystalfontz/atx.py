from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Self

AUTO_POLARITY = 0x01


class AtxPowerSwitchFunction(Enum):
    RESET_INVERT = 0x02
    POWER_INVERT = 0x04
    LCD_OFF_IF_HOST_IS_OFF = 0x10
    KEYPAD_RESET = 0x20
    KEYPAD_POWER_ON = 0x40
    KEYPAD_POWER_OFF = 0x80


@dataclass
class AtxPowerSwitchFunctionalitySettings:
    functions: Iterable[AtxPowerSwitchFunction]
    auto_polarity: bool = True
    power_pulse_length_seconds: Optional[float] = None

    def to_bytes(self: Self) -> bytes:
        functions: int = 0
        for function in self.functions:
            functions ^= function.value
        if self.auto_polarity:
            functions ^= AUTO_POLARITY

        packed: bytes = functions.to_bytes()

        if self.power_pulse_length_seconds is not None:
            pulse_length = int(self.power_pulse_length_seconds * 32)

            if pulse_length < 1:
                raise ValueError(f"Pulse length can not be less than {1/32}")

            packed += min(pulse_length, 255).to_bytes()

        return packed
