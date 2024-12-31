from crystalfontz.packet import make_crc, parse_packet


def test_packet() -> None:
    # key action, 1, \x04, crc=\xdc\x95
    buffer = b"\x80\x01\x04\xdc\x95"
    assert parse_packet(buffer) == ((0x80, b"\x04"), b"")


def test_make_crc() -> None:
    # key action, 1, \x04, crc=\xdc\x95
    buffer = b"\x80\x01\x04\xdc\x95"

    crc = make_crc(buffer[:-2])

    assert crc == b"\xdc\x95"
