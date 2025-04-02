from typing import ClassVar, Dict, Tuple

from crystalfontz.dbus.domain.base import IndexM, PositionM, t
from crystalfontz.temperature import (
    TemperatureDigits,
    TemperatureDisplayItem,
    TemperatureUnit,
)

TemperatureDigitsT = int


class TemperatureDigitsM:
    t: ClassVar[str] = "n"

    @staticmethod
    def unpack(n_digits: TemperatureDigitsT) -> TemperatureDigits:
        if n_digits != 3 and n_digits != 5:
            raise ValueError("May display either 3 or 5 temperature digits")
        return n_digits


TemperatureUnitT = bool

TEMPERATURE_UNITS: Dict[bool, TemperatureUnit] = {
    bool(unit.value): unit for unit in TemperatureUnit
}


class TemperatureUnitM:
    t: ClassVar[str] = "b"

    @staticmethod
    def pack(unit: TemperatureUnit) -> TemperatureUnitT:
        return bool(unit.value)

    @staticmethod
    def unpack(unit: TemperatureUnitT) -> TemperatureUnit:
        return TEMPERATURE_UNITS[unit]


TemperatureDisplayItemT = Tuple[int, TemperatureDigitsT, int, int, TemperatureUnitT]


class TemperatureDisplayItemM:
    """
    Map `TemperatureDisplayItem` to and from `TemperatureDisplayItemT`
    (`Tuple[int, int, int, int, bool]`).
    """

    t: ClassVar[str] = t(IndexM, TemperatureDigitsM, PositionM, PositionM, "b")

    @staticmethod
    def pack(item: TemperatureDisplayItem) -> TemperatureDisplayItemT:
        """
        Pack `TemperatureDisplayItem` to `TemperatureDisplayItemT`.
        """

        return (
            item.index,
            item.n_digits,
            item.column,
            item.row,
            TemperatureUnitM.pack(item.units),
        )

    @staticmethod
    def unpack(
        item: TemperatureDisplayItemT,
    ) -> TemperatureDisplayItem:
        """
        Unpack `TemperatureDisplayItemT` to `TemperatureDisplayItem`.
        """

        index, n_digits, column, row, units = item
        return TemperatureDisplayItem(
            index,
            TemperatureDigitsM.unpack(n_digits),
            column,
            row,
            TemperatureUnitM.unpack(units),
        )
