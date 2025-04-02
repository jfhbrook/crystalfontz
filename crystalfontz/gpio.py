from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, NoReturn, Optional, Self, Tuple, Type
import warnings

GPIO_HIGH = True
GPIO_LOW = False


@dataclass
class GpioState:
    """
    Pin state & changes since last poll.

    Attributes:
        state: State at the last reading. When True, the pin was high.
        falling: At least one falling edge has been detected since the last poll.
        rising: At least one rising edge has been detected since the last poll.
    """

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
    """
    Pin function.

    - **UNUSED**: Port unused for GPIO. It will take on the default function such as
      ATX, DOW or unused.
    - **USED**: Port used for GPIO under user control.
    """

    UNUSED = 0b0000
    USED = 0b1000


class GpioDriveMode(Enum):
    """
    Pin drive mode, based on the output state.

    For details on these settings and the supported combination, refer to your
    device's datasheet.
    """

    SLOW_STRONG = 1
    FAST_STRONG = 2
    RESISTIVE = 3
    HI_Z = 4

    @classmethod
    def from_byte(
        cls: Type[Self], mode: int
    ) -> "Tuple[Optional[GpioDriveMode], Optional[GpioDriveMode]]":
        up: Optional[GpioDriveMode] = None
        down: Optional[GpioDriveMode] = None
        if mode == 0b000:
            up = GpioDriveMode.FAST_STRONG
            down = GpioDriveMode.RESISTIVE
        elif mode == 0b001:
            up = GpioDriveMode.FAST_STRONG
            down = GpioDriveMode.FAST_STRONG
        elif mode == 0b010:
            up = GpioDriveMode.HI_Z
            down = None
        elif mode == 0b011:
            up = GpioDriveMode.RESISTIVE
            down = GpioDriveMode.FAST_STRONG
        elif mode == 0b100:
            up = GpioDriveMode.SLOW_STRONG
            down = GpioDriveMode.HI_Z
        elif mode == 0b101:
            up = GpioDriveMode.SLOW_STRONG
            down = GpioDriveMode.SLOW_STRONG
        elif mode == 0b110:
            warnings.warn(f"Drive mode {mode:0b} is reserved")
        else:
            up = GpioDriveMode.HI_Z
            down = GpioDriveMode.SLOW_STRONG

        return (up, down)


class GpioSettings:
    """
    GPIO pin settings.

    Attributes:
        function (GpioFunction): The pin's function.
        mode (Optional[int]): The raw setting of the pin's modes.
        up (Optional[GpioDriveMode]): The pin's mode for drive-up.
        down (Optional[GpioDriveMode]): The pin's mode for drive-down.
    """

    def __init__(
        self: Self,
        function: GpioFunction,
        mode: Optional[int] = None,
        up: Optional[GpioDriveMode] = None,
        down: Optional[GpioDriveMode] = None,
    ) -> None:
        self.function: GpioFunction = function
        self.mode: int

        def invalid() -> NoReturn:
            raise ValueError(f"Unsupported combination up={up}, down={down}")

        if mode is not None:
            if not (0 <= mode <= 0b111):
                raise ValueError(f"Invalid mode {mode:0b}")
            self.mode = mode
            up, down = GpioDriveMode.from_byte(mode)
            return

        if up == GpioDriveMode.FAST_STRONG:
            if down == GpioDriveMode.RESISTIVE:
                self.mode = 0b000
            elif down == GpioDriveMode.FAST_STRONG:
                self.mode = 0b001
            else:
                invalid()
        elif up == GpioDriveMode.SLOW_STRONG:
            if down == GpioDriveMode.HI_Z:
                self.mode = 0b100
            elif down == GpioDriveMode.SLOW_STRONG:
                self.mode = 0b101
            else:
                invalid()
        elif up == GpioDriveMode.RESISTIVE:
            if down == GpioDriveMode.FAST_STRONG:
                self.mode = 0b011
            else:
                invalid()
        elif up == GpioDriveMode.HI_Z:
            if down is None:
                self.mode = 0b010
            elif down == GpioDriveMode.SLOW_STRONG:
                self.mode = 0b111
            else:
                invalid()
        else:
            invalid()

    def __str__(self: Self) -> str:
        return f"GpioSettings(function={self.function}, mode={self.mode:0b}"

    def to_bytes(self: Self) -> bytes:
        return (self.function.value + self.mode).to_bytes(1, "big")

    @classmethod
    def from_byte(cls: Type[Self], data: int) -> Self:
        function = GpioFunction.USED if data & 0b1000 else GpioFunction.UNUSED
        mode = data & 0b0111
        return cls(function=function, mode=mode)

    def as_dict(self: Self) -> Dict[str, Any]:
        up, down = GpioDriveMode.from_byte(self.mode)
        return dict(
            function=self.function.value,
            mode=self.mode,
            up=up.name if up is not None else None,
            down=down.name if down is not None else None,
        )

    def __repr__(self: Self) -> str:
        up, down = GpioDriveMode.from_byte(self.mode)
        repr_ = f"Function: {self.function.value}\n"
        repr_ += (
            f"Drive Mode: {up.name if up is not None else '<none>'}, "
            f"{down.name if down is not None else '<none>'}"
        )

        return repr_
