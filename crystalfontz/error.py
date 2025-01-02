class CrystalfontzError(Exception):
    """
    An error in the Crystalfontz client.
    """

    pass


class ConnectionError(CrystalfontzError):
    """
    A connection error.
    """

    pass


class CrcError(CrystalfontzError):
    """
    An error while generating a CRC.
    """

    pass


class DecodeError(CrystalfontzError):
    """
    An error while decoding incoming data.
    """

    pass


class EncodeError(CrystalfontzError):
    """
    An error while encoding outgoing data.
    """

    pass
