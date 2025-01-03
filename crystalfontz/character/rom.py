from typing import Dict, Self, Tuple

from crystalfontz.character.constants import inverse, super_minus, super_one, x_bar
from crystalfontz.error import EncodeError

SpecialCharacterRange = Tuple[int, int]


class CharacterRom:
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
                    self._table[char] = point.to_bytes()

    def __getitem__(self: Self, key: str) -> bytes:
        return self._table[key]

    def __setitem__(self: Self, key: str, value: bytes) -> None:
        self._table[key] = value

    def set_encoding(self: Self, char: str, encoded: int | bytes) -> Self:
        if isinstance(encoded, int):
            self[char] = encoded.to_bytes()
        else:
            self[char] = encoded
        return self

    def encode(self: Self, input: str, errors="strict") -> bytes:
        output: bytes = b""
        i = 0
        while i < len(input):
            char = input[i]

            # TODO: This encoder uses if/else statements to handle multi-byte
            # encodings. To make this general purpose, it needs to be
            # refactored to use a trie-like structure.
            if char == "x":
                if input[i + 1] == x_bar[1] and input[i + 2] == x_bar[2]:
                    output += self._table[x_bar]
                    i += 2
                else:
                    output += self._table["x"]
            elif char in self._table:
                output += self._table[char]
            elif char == super_minus:
                if input[i + 1] == super_one:
                    output += self._table[inverse]
                    i += 1
            else:
                if errors == "strict":
                    raise EncodeError(f"Unknown character {char}")
                else:
                    output += self._table["*"]

            i += 1

        return output

    def set_special_character_range(self: Self, start: int, end: int) -> Self:
        self.special_character_range = (start, end)
        return self

    def validate_special_character_index(self: Self, index: int) -> Self:
        left, right = self.special_character_range
        if not (left <= index <= right):
            raise ValueError(f"{index} is outside range [{left}, {right}]")
        return self
