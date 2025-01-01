import pytest

from crystalfontz.character import encode_chars, ENCODE_TABLE

# Manually encoded characters
exc = 32 + 1
_ = 32 + 0
H = 64 + 8
d = 96 + 4
e = 96 + 5
l = 96 + 12
o = 96 + 15
r = 112 + 2
w = 112 + 7


def test_encode_table() -> None:
    assert ENCODE_TABLE["!"] == exc.to_bytes()


@pytest.mark.parametrize(
    "input,expected", [("Hello world!", bytes([H, e, l, l, o, _, w, o, r, l, d, exc]))]
)
def test_encode_chars(input, expected) -> None:
    assert encode_chars(input) == expected
