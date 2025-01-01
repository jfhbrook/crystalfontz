from typing import Dict, Tuple

from crystalfontz.error import EncodeError

#
# This ROM encoding is based on page 44 of this doc:
#
#     file:///Users/josh/Downloads/CFA533-TMI-KU.pdf
#
# However, it is *incomplete*, mostly because I don't know katakana and only
# know a smattering of Greek. Characters that I don't know the glyph to are
# filled in with _ characters, and some characters that *are* filled out are
# best guesses.
#
# There is also exactly one character, a ^-1 character (inverse), that doesn't
# have a single unicode character. That character is special cased in the serializer.
#
# TODO: This ROM might also be device specific.
#

# ^{-1}
inv = "\u207b\u00B9"
hbar = "―"
japan_interpunct = "・"
japan_lquote = "「"
japan_rquote = "」"
japan_full_stop = "。"
japan_comma = "、"

CGROM = """
  0@P`p   ―__α_
 !1AQaq  。ア__ä_
 "2BRbr  「_ツ_βθ
 #3CScs  」ウ__ε∞
 $4DTdt  、エ__μΩ
 %5EUeu  ・オ__σü
 &6FVfv  ヲカ___ρΣ
 '7GWgw  アキ___π
 (8HXhx  イク__√x̄
 )9IYiy  ゥケ____
 *:JZjz  エコ_____
 +;K[k{  オサ____
 ,<L¥l|  ヤシ__¢_
 -=M]m}  ユヌ__£÷
 .>N^n→  ヨセ__ñ 
 /?O_o←  ツソ_°ö█
"""

ENCODE_TABLE: Dict[str, int] = dict()

i = 0

for row in CGROM.split("\n")[1:-1]:
    j = 0
    for char in row:
        ENCODE_TABLE[char] = j * 16 + i
        j += 1
    i += 1


def encode_chars(input: str, errors="strict") -> Tuple[bytes, int]:
    output: bytes = b""
    i = 0
    while i < len(input):
        char = input[i]
        # Special case
        if char == "_":
            if errors == "strict":
                raise EncodeError(f"Unknown character {char}")
        elif char in ENCODE_TABLE:
            output = ENCODE_TABLE[char].to_bytes()
        elif char == "\u207b":
            # Special case ^{-1}. I don't know if this is the idiomatic way
            # to type this.
            if input[i + 1] == "\u00B9":
                output += (233).to_bytes()
                i += 1
        else:
            if errors == "strict":
                raise EncodeError(f"Unknown character {char}")

        i += 1

    return output, len(output)
