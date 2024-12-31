from crystalfontz.packet import parse_packet, make_crc

def test_packet() -> None:
    # key action, 1, \x04, crc=\xdc\x95
    buffer = b'\x80\x01\x04\xdc\x95'
    assert parse_packet(buffer) == ((0x80, 0x04), b"")


def test_make_crc() -> None:
    # key action, 1, \x04, crc=\xdc\x95
    buffer = b'\x80\x01\x04\xdc\x95'

    crc = make_crc(make_crc(buffer[:-2]))

    assert crc == b"\xdc\x95"

