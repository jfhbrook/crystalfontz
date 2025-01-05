import pytest

from crystalfontz.character import inverse, SMILEY_FACE, x_bar
from crystalfontz.device import CFA533, CFA533_CHARACTER_ROM

# Manually encoded characters
exclamation = 32 + 1
_ = 32 + 0
H = 64 + 8
d = 96 + 4
e = 96 + 5
l = 96 + 12  # noqa: E741
o = 96 + 15
r = 112 + 2
w = 112 + 7


@pytest.mark.parametrize("decoded,encoded", [("!", exclamation)])
def test_encode_table(decoded, encoded) -> None:
    assert CFA533_CHARACTER_ROM[decoded] == encoded.to_bytes(length=1)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Hello world!", bytes([H, e, l, l, o, _, w, o, r, l, d, exclamation])),
        (inverse, bytes([224 + 9])),
        (x_bar, bytes([240 + 8])),
    ],
)
def test_encode(input, expected) -> None:
    assert CFA533_CHARACTER_ROM.encode(input) == expected


@pytest.mark.parametrize("special_character", [SMILEY_FACE])
def test_special_character_valid(special_character):
    device = CFA533()
    special_character.validate(device)
    encoded: bytes = special_character.as_bytes(device)
    # 0x09 takes 9 bytes of data. The first character is the index (0-7) and
    # the actual character is 8 bytes.
    assert len(encoded) == 8, "Special character should be eight bytes"
    for n in encoded:
        assert n <= 63, f"Byte {n} ({n:0b}) > 63"
