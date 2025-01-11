import pytest

from crystalfontz.cli import parse_bytes


@pytest.mark.parametrize(
    "text,buffer",
    [
        ("hello world", b"hello world"),
        ("\\\\", b"\\"),
        ("\\a", b"\a"),
        ("\\o333", (0o333).to_bytes(1, byteorder="big")),
        ("\\o22", (0o22).to_bytes(1, byteorder="big")),
        ("\\xff", b"\xff"),
        ("\\", b"\\"),
        ("\\s", b"\\s"),
        ("\\xf", b"\\xf"),
    ],
)
@pytest.mark.filterwarnings("ignore:invalid escape sequence")
def test_parse_bytes(text, buffer) -> None:
    assert parse_bytes(text) == buffer
