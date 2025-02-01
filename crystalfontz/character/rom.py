from typing import Dict, Self, Tuple

from crystalfontz.error import EncodeError

SpecialCharacterRange = Tuple[int, int]
MAX_UNICODE_BYTES = 4


class CharacterRom:
    """
    A character ROM (CGROM). A character ROM contains 5x7 glyphs stored at
    specified addresses. The first 8 addresses are reserved for storing special
    characters in RAM.

    For more information, refer to your device's datasheet.

    Parameters:
        sheet: A multi-line string containing characters encoded in the character ROM.
    """

    def __init__(self: Self, sheet: str) -> None:
        self.special_character_range: SpecialCharacterRange = (0, 7)
        self._table: Dict[str, bytes] = dict()

        lines = sheet.split("\n")
        if lines[0] == "":
            lines = lines[1:]
        if lines[-1] == "":
            lines = lines[0:-1]

        for i, row in enumerate(lines):
            for j, char in enumerate(row):
                point = (16 * j) + i
                if char != " " or point == 32:
                    self._table[char] = point.to_bytes(1, "big")

    def __getitem__(self: Self, key: str) -> bytes:
        return self._table[key]

    def __setitem__(self: Self, key: str, value: bytes) -> None:
        self._table[key] = value

    def set_encoding(self: Self, char: str, encoded: int | bytes) -> Self:
        """
        Set how a unicode character is encoded into a byte. This is used to allow the
        encoding of special characters.
        """

        if isinstance(encoded, int):
            self[char] = encoded.to_bytes(1, "big")
        else:
            self[char] = encoded
        return self

    def encode(self: Self, input: str, errors="strict") -> bytes:
        """
        Encode a unicode string into bytes, which correspond to the locations in your
        device's character ROM.
        """

        output: bytes = b""
        i = 0
        while i < len(input):
            n = MAX_UNICODE_BYTES
            char = input[i : i + n]

            while n > 0:
                if char in self._table:
                    output += self._table[char]
                    break
                else:
                    n -= 1
                    char = input[i : i + n]

            if not n:
                if errors == "strict":
                    raise EncodeError(f"Unknown character {char}")
                else:
                    n = 1
                    output += self._table["*"]

            i += n

        return output

    def set_special_character_range(self: Self, start: int, end: int) -> Self:
        self.special_character_range = (start, end)
        return self

    def validate_special_character_index(self: Self, index: int) -> Self:
        left, right = self.special_character_range
        if not (left <= index <= right):
            raise ValueError(f"{index} is outside range [{left}, {right}]")
        return self
