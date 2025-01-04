from dataclasses import dataclass
from enum import Enum
from typing import NoReturn, Optional, Self, Type
import warnings

GPIO_HIGH = True
GPIO_LOW = False


@dataclass
class GpioState:
    state: bool
    falling: bool
    rising: bool

    @classmethod
    def from_byte(cls: Type[Self], data: int) -> Self:
        return cls(
            state=bool(data & 0b0001),
            falling=bool(data & 0b0010),
            rising=bool(data & 0b0100),
        )


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

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        if len(data) != 1:
            raise ValueError("GPIO settings expected to be 8 bits")

        function = GpioFunction.USED if data[0] & 0b1000 else GpioFunction.UNUSED
        mode = data[0] & 0b0111
        when_up: Optional[GpioDriveMode] = None
        when_down: Optional[GpioDriveMode] = None
        if mode == 0b000:
            when_up = GpioDriveMode.FAST_STRONG
            when_down = GpioDriveMode.RESISTIVE
        elif mode == 0b001:
            when_up = GpioDriveMode.FAST_STRONG
            when_down = GpioDriveMode.FAST_STRONG
        elif mode == 0b010:
            when_up = GpioDriveMode.HI_Z
            when_down = None
        elif mode == 0b011:
            when_up = GpioDriveMode.RESISTIVE
            when_down = GpioDriveMode.FAST_STRONG
        elif mode == 0b100:
            when_up = GpioDriveMode.SLOW_STRONG
            when_down = GpioDriveMode.HI_Z
        elif mode == 0b101:
            when_up = GpioDriveMode.SLOW_STRONG
            when_down = GpioDriveMode.SLOW_STRONG
        elif mode == 0b110:
            warnings.warn(f"Drive mode {mode:0b} is reserved")
        else:
            when_up = GpioDriveMode.HI_Z
            when_down = GpioDriveMode.SLOW_STRONG

        return cls(function=function, mode=mode, when_up=when_up, when_down=when_down)
