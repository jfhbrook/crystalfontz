from typing import ClassVar, Dict, Literal, Tuple

from crystalfontz.dbus.map.base import IndexM, PositionM, t
from crystalfontz.temperature import TemperatureDisplayItem, TemperatureUnit


class TemperatureDigitsM:
    t: ClassVar[str] = "n"

    @staticmethod
    def unpack(n_digits: int) -> Literal[3] | Literal[5]:
        if n_digits != 3 or n_digits != 5:
            raise ValueError("May display either 3 or 5 temperature digits")
        return n_digits


TEMPERATURE_UNITS: Dict[bool, TemperatureUnit] = {
    bool(unit.value): unit for unit in TemperatureUnit
}


class TemperatureUnitM:
    t: ClassVar[str] = "b"

    @staticmethod
    def unpack(unit: bool) -> TemperatureUnit:
        return TEMPERATURE_UNITS[unit]

    @staticmethod
    def pack(unit: TemperatureUnit) -> bool:
        return bool(unit.value)


class TemperatureDisplayItemM:
    t: ClassVar[str] = t(IndexM, TemperatureDigitsM, PositionM, PositionM, "b")

    @staticmethod
    def unpack(
        item: Tuple[int, int, int, int, bool],
    ) -> TemperatureDisplayItem:

        index, n_digits, column, row, units = item
        return TemperatureDisplayItem(
            index,
            TemperatureDigitsM.unpack(n_digits),
            column,
            row,
            TemperatureUnitM.unpack(units),
        )

    @staticmethod
    def pack(item: TemperatureDisplayItem) -> Tuple[int, int, int, int, bool]:
        return (
            item.index,
            item.n_digits,
            item.column,
            item.row,
            TemperatureUnitM.pack(item.units),
        )
