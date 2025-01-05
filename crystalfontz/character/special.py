from typing import Any, List, Protocol, Type

try:
    from typing import Self
except ImportError:
    Self = Any


from bitstring import BitArray


class DeviceProtocol(Protocol):
    character_height: int
    character_width: int


class SpecialCharacter:
    """
    A representation of a "special character" - this is a user-defined
    character that can be stored in user flash.
    """

    def __init__(self: Self, pixels: List[List[int]]) -> None:
        self.pixels: List[List[int]] = pixels

    @classmethod
    def from_str(cls: Type[Self], character: str) -> Self:

        lines = character.split("\n")
        if lines[0] == "":
            lines = lines[1:]
        if lines[-1] == "":
            lines = lines[0:-1]

        pixels: List[List[int]] = [
            [0 if c == " " else 1 for c in line] for line in lines
        ]

        width = max([len(row) for row in pixels])
        pixels = [row + [0 for _ in range(0, width - len(row))] for row in pixels]

        return cls(pixels)

    def as_bytes(self: Self, device: DeviceProtocol) -> bytes:
        character: BitArray = BitArray()

        for i, row in enumerate(self.pixels):
            if i >= device.character_height:
                break
            character += f"0b{'0' * (8 - device.character_width)}"
            for pixel in row[0 : device.character_width]:
                character += "0b1" if pixel else "0b0"

        return character.tobytes()

    def validate(self: Self, device: DeviceProtocol) -> None:
        height: int = len(self.pixels)
        width: int = len(self.pixels[0])

        if width != device.character_width or height != device.character_height:
            raise ValueError(
                f"Character should be {device.character_width} × "
                f"{device.character_height} pixels, is {width} × {height}"
            )


SMILEY_FACE = SpecialCharacter.from_str(
    """
      
  xxx 
 x x x
 x x x
 xxxxx
 x x x
 xx xx
  xxx 
"""  # noqa: W291, W293
)
