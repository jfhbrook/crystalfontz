from typing import ClassVar

from crystalfontz.character import SpecialCharacter


class SpecialCharacterM:
    t: ClassVar[str] = "t"

    @staticmethod
    def unpack(character: int) -> SpecialCharacter:
        raise NotImplementedError("load")
