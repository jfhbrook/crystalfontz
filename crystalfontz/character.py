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
# TODO: This ROM might be device specific.
#

# Characters that take more than one code point in unicode. These characters
# are special cased in the encoder.
super_minus = "\u207b"
super_one = "\u00B9"
inv = f"{super_minus}{super_one}"
x_bar = "x̄"

# Characters which only require one code point, but are difficult to type
# and/or are ambiguous.
hbar = "―"  # Intended to be a katakana character?
block = "█"

# Japanese punctuation
japan_interpunct = "・"
japan_lquote = "「"
japan_rquote = "」"
japan_full_stop = "。"
japan_comma = "、"

# Unknown characters, as well as characters known to take multiple code points,
# are represented as _.
# NOTE: ascii characters generally share their code points with true ASCII.
# TODO: Does this ROM match another encoding which contains both Katakana and
# Greek letters?
CGROM = """
  0@P`p   ―__α_
 !1AQaq  。ア__ä_
 "2BRbr  「_ツ_βθ
 #3CScs  」ウ__ε∞
 $4DTdt  、エ__μΩ
 %5EUeu  ・オ__σü
 &6FVfv  ヲカ__ρΣ
 '7GWgw  アキ___π
 (8HXhx  イク__√_
 )9IYiy  ゥケ____
 *:JZjz  エコ_____
 +;K[k{  オサ____
 ,<L¥l|  ヤシ__¢_
 -=M]m}  ユヌ__£÷
 .>N^n→  ヨセ__ñ 
 /?O_o←  ツソ_°ö█
"""

ENCODE_TABLE: Dict[str, bytes] = dict()

for i, row in enumerate(CGROM.split("\n")[1:-1]):
    for j, char in enumerate(row):
        if char != "_":
            ENCODE_TABLE[char] = (((j + 1) * 16) + i).to_bytes()

# Multi-point characters - we keep these in the lookup table but encode them
# "directly".
ENCODE_TABLE[inv] = (244 + 9).to_bytes()
ENCODE_TABLE[x_bar] = (240 + 8).to_bytes()

# Multiple locations in the ROM are blank, so pick the one corresponding to
# ASCII
ENCODE_TABLE[" "] = b" "
# We used _ as a placeholder, so set its actual ASCII encoding (oops)
ENCODE_TABLE["_"] = b"_"

# TODO: The first 7 points in the CGROM are labeled "CGRAM" and might be
# customizable as user flash?


def encode_chars(input: str, errors="strict") -> bytes:
    output: bytes = b""
    i = 0
    while i < len(input):
        char = input[i]

        if char == "x":
            if input[i + 1] == x_bar[1] and input[i + 2] == x_bar[2]:
                output += ENCODE_TABLE[x_bar]
                i += 2
            else:
                output += ENCODE_TABLE["x"]
        elif char in ENCODE_TABLE:
            output += ENCODE_TABLE[char]
        elif char == super_minus:
            # Special case for inverse
            if input[i + 1] == super_one:
                output += ENCODE_TABLE[inv]
                # consume two characters, not just one
                i += 1
        else:
            if errors == "strict":
                raise EncodeError(f"Unknown character {char}")
            else:
                output += ENCODE_TABLE["*"]

        i += 1

    return output
