from typing import Dict, Self

from crystalfontz.error import EncodeError

"""
Abstractions for representing character ROMs (CGROMs), and encoding text to be
used with them.
"""

# Characters that take more than one code point in unicode. These need to be
# manually added to the character ROM.
super_minus: str = "\u207b"
super_one: str = "\u00B9"
inverse: str = f"{super_minus}{super_one}"
x_bar: str = "x̄"

# Characters which only require one code point, but are difficult to type
# and/or are ambiguous.
hbar = "―"  # Intended to be a katakana character?
block = "█"

# Japanese punctuation. The CFA533, at least, contains Katakana characters
# with corresponding punctuation.
japan_interpunct = "・"
japan_lquote = "「"
japan_rquote = "」"
japan_full_stop = "。"
japan_comma = "、"


class CgRom:
    def __init__(self: Self, sheet: str) -> None:
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


#
# This ROM encoding is based on page 44 of this doc:
#
#     file:///Users/josh/Downloads/CFA533-TMI-KU.pdf
#
# However, it is *incomplete*, mostly because I don't know katakana and only
# know a smattering of Greek. Unknown characters are filled in with spaces.
# Some characters that *are* filled out are best guesses.
#
# NOTE: ASCII characters generally share their code points with true ASCII.
# TODO: Does this ROM match another encoding which contains both katakana and
# Greek letters?
# NOTE: The first column in the ROM is reserved for custom characters.
#

ROM = (
    CgRom(
        """
   0@P`p   ―  α 
  !1AQaq  。ア  ä 
  "2BRbr  「 ツ βθ
  #3CScs  」ウ  ε∞
  $4DTdt  、エ  μΩ
  %5EUeu  ・オ  σü
  &6FVfv  ヲカ  ρΣ
  '7GWgw  アキ   π
  (8HXhx  イク  √ 
  )9IYiy  ゥケ    
  *:JZjz  エコ     
  +;K[k{  オサ    
  ,<L¥l|  ヤシ  ¢ 
  -=M]m}  ユヌ  £÷
  .>N^n→  ヨセ  ñ 
  /?O_o←  ツソ °ö█
"""
    )
    .set_encoding(inverse, 244 + 9)
    .set_encoding(x_bar, 240 + 8)
)


# TODO: This encoding is likely device specific. I'm leaving it in here for
# now because the encode method contains logic specific to the device. However,
# once that is factored out in favor of a trie-like data structure, this
# specific instance should be moved to device.py.
encode_chars = ROM.encode
