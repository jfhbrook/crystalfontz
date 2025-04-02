from typing import ClassVar

from crystalfontz.character import SpecialCharacter

SpecialCharacterT = int


class SpecialCharacterM:
    t: ClassVar[str] = "t"

    @staticmethod
    def unpack(character: SpecialCharacterT) -> SpecialCharacter:
        raise NotImplementedError("load")
