from typing import ClassVar, Dict

from crystalfontz.lcd import LcdRegister

LCD_REGISTERS: Dict[bool, LcdRegister] = {
    bool(register.value): register for register in LcdRegister
}


class LcdRegisterM:
    """
    Map LcdRegister to and from dbus types.
    """

    t: ClassVar[str] = "b"

    @staticmethod
    def unpack(register: bool) -> LcdRegister:
        return LCD_REGISTERS[register]

    @staticmethod
    def pack(register: LcdRegister) -> bool:
        return bool(register.value)
