from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Literal, Optional, Protocol, Self, Set, Type


class DeviceProtocol(Protocol):
    lines: int
    columns: int
    n_temperature_sensors: int


class TemperatureUnit(Enum):
    """
    A temperature unit. Either CELSIUS or FAHRENHEIT.
    """

    CELSIUS = 0
    FAHRENHEIT = 1


TemperatureDigits = Literal[3] | Literal[5]


@dataclass
class TemperatureDisplayItem:
    """
    A temperature display item, as used in command 21 (0x15): Set Up Live
    Temperature Display.

    Parameters:
        index (int): The index of the display item.
        n_digits (Literal[3] | Literal[5]): The number of digits to display.
        column (int): The zero-indexed column to display the temperature on.
        row (int): The zero-indexed row to display the temperature on.
        units (TemperatureUnit): The units to use when displaying the temperature.
    """

    index: int
    # TODO: Device specific?
    n_digits: TemperatureDigits
    column: int
    row: int
    units: TemperatureUnit

    @classmethod
    def to_bytes(
        cls: Type[Self], item: Optional[Self], device: DeviceProtocol
    ) -> bytes:
        if item is None:
            return b"\x00"
        # TODO: Validation. The documentation suggests that sensors 32+ are
        # actually for something else - fan speed?
        index: bytes = item.index.to_bytes(1, "big")
        n_digits: bytes = item.n_digits.to_bytes(1, "big")

        if not (0 <= item.column < device.columns):
            raise ValueError(f"Column {item.column} is invalid")

        column: bytes = item.column.to_bytes(1, "big")

        if not (0 <= item.row < device.lines):
            raise ValueError(f"Row {item.row} is invalid")

        row: bytes = item.row.to_bytes(1, "big")
        units: bytes = item.units.value.to_bytes(1, "big")

        return index + n_digits + column + row + units


def pack_temperature_settings(enabled: Iterable[int], device: DeviceProtocol) -> bytes:
    bs: List[int] = [0 for _ in range(0, device.n_temperature_sensors // 8)]
    for sensor in set(enabled):
        sensor_idx = sensor - 1
        bytes_idx: int = sensor_idx // 8
        mask: int = 0b00000001 << (sensor_idx - (bytes_idx * 8))
        bs[bytes_idx] ^= mask

    return bytes(bs)


def unpack_temperature_settings(settings: bytes) -> Set[int]:
    unpacked: Set[int] = set()

    for byte_idx, byte in enumerate(settings):
        for bit_idx in range(0, 8):
            sensor_idx = 8 * byte_idx + (8 - bit_idx)
            mask = 0b10000000 >> bit_idx
            if byte & mask:
                unpacked.add(sensor_idx)

    return unpacked
