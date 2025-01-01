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


class ParseError(CrystalfontzError):
    """
    An error while parsing incoming data.
    """

    pass


class EncodeError(CrystalfontzError):
    """
    An error while encoding text.
    """

    pass


class SerializationError(CrystalfontzError):
    """
    An error while serializing data.
    """

    pass
