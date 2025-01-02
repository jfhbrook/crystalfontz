from typing import Self, Tuple, Type


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


class UnknownResponseError(DecodeError):
    """
    An error raised when the response code is unrecognized.
    """

    def __init__(self: Self, packet: Tuple[int, bytes]) -> None:
        code, payload = packet

        self.code = code
        self.payload = payload

        super().__init__(f"Unknown response ({code}, {payload})")


class DeviceError(CrystalfontzError):
    """
    An error returned from the device.
    """

    @classmethod
    def is_error_code(cls: Type[Self], code: int) -> bool:
        # Error codes start with bits 0b11
        return code >> 6 == 0b11

    def __init__(self: Self, packet: Tuple[int, bytes]) -> None:
        code, payload = packet
        # The six bits following the 0b11 correspond to the command
        self.command = code & 0o77
        self.payload = payload
        message = f"Error executing command {self.command}"

        if len(self.payload):
            message += f": {self.payload}"

        super().__init__(message)
