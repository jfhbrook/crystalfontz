from enum import Enum
from typing import NoReturn, Optional, Self


class GpioFunction(Enum):
    UNUSED = 0b0000
    USED = 0b1000


class GpioDriveMode(Enum):
    SLOW_STRONG = 1
    FAST_STRONG = 2
    RESISTIVE = 3
    HI_Z = 4


class GpioSettings:
    def __init__(
        self: Self,
        function: GpioFunction,
        mode: Optional[int] = None,
        when_up: Optional[GpioDriveMode] = None,
        when_down: Optional[GpioDriveMode] = None,
    ) -> None:
        self.function: GpioFunction = function
        self.mode: int

        def invalid() -> NoReturn:
            raise ValueError(
                f"Unsupported combination when_up={when_up}, when_down={when_down}"
            )

        if mode:
            if not (0 <= mode <= 0b111):
                raise ValueError(f"Invalid mode {mode:0b}")
            self.mode = mode
            return

        if when_up == GpioDriveMode.FAST_STRONG:
            if when_down == GpioDriveMode.RESISTIVE:
                self.mode = 0b000
            elif when_down == GpioDriveMode.FAST_STRONG:
                self.mode = 0b001
            else:
                invalid()
        elif when_up == GpioDriveMode.SLOW_STRONG:
            if when_down == GpioDriveMode.HI_Z:
                self.mode = 0b100
            elif when_down == GpioDriveMode.SLOW_STRONG:
                self.mode = 0b101
            else:
                invalid()
        elif when_up == GpioDriveMode.RESISTIVE:
            if when_down == GpioDriveMode.FAST_STRONG:
                self.mode = 0b011
            else:
                invalid()
        elif when_up == GpioDriveMode.HI_Z:
            if when_down == None:
                self.mode = 0b010
            elif when_down == GpioDriveMode.SLOW_STRONG:
                self.mode = 0b111
            else:
                invalid()
        else:
            invalid()

    def __str__(self: Self) -> str:
        return f"GpioSettings(function={self.function}, mode={self.mode:0b}"

    def to_bytes(self: Self) -> bytes:
        return (self.function.value + self.mode).to_bytes()
