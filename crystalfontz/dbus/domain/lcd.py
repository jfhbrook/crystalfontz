from typing import ClassVar, Dict

from crystalfontz.lcd import LcdRegister

LcdRegisterT = bool

LCD_REGISTERS: Dict[bool, LcdRegister] = {
    bool(register.value): register for register in LcdRegister
}


class LcdRegisterM:
    """
    Map `LcdRegister` to and from `LcdRegisterT` (`bool`).
    """

    t: ClassVar[str] = "b"

    @staticmethod
    def pack(register: LcdRegister) -> LcdRegisterT:
        return bool(register.value)

    @staticmethod
    def unpack(register: LcdRegisterT) -> LcdRegister:
        return LCD_REGISTERS[register]
