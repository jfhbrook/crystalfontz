from typing import Any, Optional, Self, Tuple, Type


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


class ResponseDecodeError(DecodeError):
    """
    An error while decoding a response.
    """

    def __init__(self: Self, response_cls: Type[Any], message: str) -> None:
        super().__init__(message)
        self.response_cls: Type[Any] = response_cls


class EncodeError(CrystalfontzError):
    """
    An error while encoding outgoing data.
    """

    pass


class DeviceLookupError(CrystalfontzError):
    """
    An error while looking up a device.
    """

    pass


class UnknownResponseError(DecodeError):
    """
    An error raised when the response code is unrecognized.
    """

    def __init__(self: Self, packet: Tuple[int, bytes]) -> None:
        code, payload = packet

        self.code: int = code
        self.command_code: Optional[int] = code - 0x40 if code < 0x80 else None
        self.payload = payload

        super().__init__(f"Unknown response (0x{code:02X}, {payload})")


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
        # The expected response code, so we can match this error with the
        # expected success response
        self.expected_response = self.command + 0x40
        self.payload = payload
        message = f"Error executing command 0x{self.command:02X}"

        if len(self.payload):
            message += f": {self.payload}"

        super().__init__(message)
