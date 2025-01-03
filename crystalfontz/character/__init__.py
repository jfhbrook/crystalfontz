from crystalfontz.character.constants import (
    block,
    hbar,
    inverse,
    japan_comma,
    japan_full_stop,
    japan_interpunct,
    japan_lquote,
    japan_rquote,
    x_bar,
)
from crystalfontz.character.rom import CharacterRom
from crystalfontz.character.special import SpecialCharacter

#
# This ROM encoding is based on page 44 of CFA533-TMI-KU.pdf.
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

CHARACTER_ROM = (
    CharacterRom(
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
encode_chars = CHARACTER_ROM.encode

__all__ = [
    "inverse",
    "x_bar",
    "hbar",
    "block",
    "japan_interpunct",
    "japan_lquote",
    "japan_rquote",
    "japan_full_stop",
    "japan_comma",
    "CharacterRom",
    "SpecialCharacter",
    "encode_chars",
]
