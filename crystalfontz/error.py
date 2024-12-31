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


class ParseError(CrystalfontzError):
    """
    An error while parsing incoming data.
    """

    pass


class SerializationError(CrystalfontzError):
    """
    An error while serializing data.
    """

    pass
