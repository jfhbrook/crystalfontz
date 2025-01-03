from typing import List, Protocol, Self, Type

from bitstring import BitArray


class DeviceProtocol(Protocol):
    character_height: int
    character_width: int


class SpecialCharacter:
    """
    A representation of a "special character" - this is a user-defined
    character that can be stored in user flash.
    """

    def __init__(self: Self, character: List[BitArray]) -> None:
        self.character: List[BitArray] = character

    @classmethod
    def from_str(cls: Type[Self], character: str) -> Self:

        lines = character.split("\n")
        if lines[0] == "":
            lines = lines[1:]
        if lines[-1] == "":
            lines = lines[0:-1]

        char: List[BitArray] = list()

        for line in lines:
            buffer: BitArray = BitArray()
            for c in line:
                if c == " ":
                    buffer += "0b0"
                else:
                    buffer += "0b1"
            char.append(buffer)

        return cls(char)

    def as_bytes(self: Self, device: DeviceProtocol) -> bytes:
        self.validate(device)
        return b"".join([row.tobytes() for row in self.character])

    def validate(self: Self, device: DeviceProtocol) -> None:
        if len(self.character) != device.character_height:
            raise ValueError(
                f"Character {len(self.character)} pixels tall, should be "
                f"{device.character_height}"
            )
        for i, row in enumerate(self.character):
            if len(row) != device.character_width:
                raise ValueError(
                    f"Row {i} is {len(row)} pixels wide, should be "
                    f"{device.character_width}"
                )


SMILEY_FACE = SpecialCharacter.from_str(
    """
        
 xxxxxx 
xx xx xx
xx xx xx
xxxxxxxx
x xxxx x
xx    xx
 xxxxxx 
"""
)
